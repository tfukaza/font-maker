"""Strict SVG inspection, safe normalization, and outline extraction."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, ElementTree, SubElement

from defusedxml import ElementTree as SafeET
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import decomposeQuadraticSegment
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

from .errors import FontMakerError
from .models import SvgContract

MAX_SVG_BYTES = 1_000_000
MAX_PATH_OPERATIONS = 25_000
SVG_NS = "http://www.w3.org/2000/svg"
ALLOWED_ARTWORK = {"g", "path", "rect", "circle", "ellipse", "polygon"}
REJECTED_ELEMENTS = {
    "script",
    "style",
    "text",
    "image",
    "use",
    "foreignObject",
    "filter",
    "mask",
    "clipPath",
    "pattern",
}
TRANSFORM_RE = re.compile(r"([A-Za-z]+)\s*\(([^)]*)\)")
NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass(frozen=True)
class NormalizedSvg:
    content: bytes
    path_data: tuple[str, ...]
    bounds: tuple[float, float, float, float] | None
    operation_count: int
    fixes: tuple[str, ...]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _number(element: Element, name: str, *, default: float | None = None) -> float:
    raw = element.get(name)
    if raw is None:
        if default is None:
            raise FontMakerError("INVALID_SVG", f"<{_local_name(element.tag)}> requires {name}")
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise FontMakerError("INVALID_SVG", f"Invalid numeric {name}={raw!r}") from exc
    if not math.isfinite(value):
        raise FontMakerError("INVALID_SVG", f"Non-finite numeric {name}={raw!r}")
    return value


def _number_list(raw: str, context: str) -> list[float]:
    remainder = NUMBER_RE.sub("", raw)
    if re.sub(r"[\s,]+", "", remainder):
        raise FontMakerError("INVALID_SVG", f"Invalid numeric data in {context}: {raw}")
    values = [float(match.group(0)) for match in NUMBER_RE.finditer(raw)]
    if not all(math.isfinite(value) for value in values):
        raise FontMakerError("INVALID_SVG", f"Non-finite numeric data in {context}")
    return values


def _parse_transform(raw: str | None) -> Transform:
    if not raw:
        return Transform()
    matches = list(TRANSFORM_RE.finditer(raw))
    remainder = TRANSFORM_RE.sub("", raw).strip(" ,\t\r\n")
    if not matches or remainder:
        raise FontMakerError("INVALID_SVG", f"Unsupported transform: {raw}")
    transform = Transform()
    for match in matches:
        name = match.group(1)
        values = _number_list(match.group(2), "transform")
        if name == "matrix" and len(values) == 6:
            operation = Transform(*values)
        elif name == "translate" and len(values) in {1, 2}:
            operation = Transform().translate(values[0], values[1] if len(values) == 2 else 0)
        elif name == "scale" and len(values) in {1, 2}:
            operation = Transform().scale(values[0], values[1] if len(values) == 2 else values[0])
        elif name == "rotate" and len(values) in {1, 3}:
            angle = math.radians(values[0])
            if len(values) == 3:
                cx, cy = values[1:]
                operation = Transform().translate(cx, cy).rotate(angle).translate(-cx, -cy)
            else:
                operation = Transform().rotate(angle)
        elif name == "skewX" and len(values) == 1:
            operation = Transform().skew(math.radians(values[0]))
        else:
            raise FontMakerError(
                "INVALID_SVG", f"Unsupported transform operation: {match.group(0)}"
            )
        transform = transform.transform(operation)
    return transform


def _primitive_path(element: Element) -> str:
    kind = _local_name(element.tag)
    if kind == "path":
        data = element.get("d", "").strip()
        if not data:
            raise FontMakerError("INVALID_SVG", "Artwork path has no path data")
        return data
    if kind == "rect":
        if _number(element, "rx", default=0) or _number(element, "ry", default=0):
            raise FontMakerError("INVALID_SVG", "Rounded rectangles must be converted to paths")
        x = _number(element, "x", default=0)
        y = _number(element, "y", default=0)
        width = _number(element, "width")
        height = _number(element, "height")
        if width <= 0 or height <= 0:
            raise FontMakerError("INVALID_SVG", "Rectangle dimensions must be positive")
        return f"M{x:g} {y:g}H{x + width:g}V{y + height:g}H{x:g}Z"
    if kind in {"circle", "ellipse"}:
        cx = _number(element, "cx", default=0)
        cy = _number(element, "cy", default=0)
        rx = _number(element, "r" if kind == "circle" else "rx")
        ry = rx if kind == "circle" else _number(element, "ry")
        if rx <= 0 or ry <= 0:
            raise FontMakerError("INVALID_SVG", "Ellipse radii must be positive")
        k = 0.5522847498307936
        return (
            f"M{cx + rx:g} {cy:g}"
            f"C{cx + rx:g} {cy + k * ry:g} {cx + k * rx:g} {cy + ry:g} {cx:g} {cy + ry:g}"
            f"C{cx - k * rx:g} {cy + ry:g} {cx - rx:g} {cy + k * ry:g} {cx - rx:g} {cy:g}"
            f"C{cx - rx:g} {cy - k * ry:g} {cx - k * rx:g} {cy - ry:g} {cx:g} {cy - ry:g}"
            f"C{cx + k * rx:g} {cy - ry:g} {cx + rx:g} {cy - k * ry:g} {cx + rx:g} {cy:g}Z"
        )
    if kind == "polygon":
        values = _number_list(element.get("points", ""), "polygon points")
        if len(values) < 6 or len(values) % 2:
            raise FontMakerError("INVALID_SVG", "Polygon needs at least three coordinate pairs")
        points = list(zip(values[::2], values[1::2], strict=True))
        return "M" + "L".join(f"{x:g} {y:g}" for x, y in points) + "Z"
    raise FontMakerError("INVALID_SVG", f"Unsupported artwork element: <{kind}>")


def _validate_attributes(element: Element) -> None:
    kind = _local_name(element.tag)
    for name, value in element.attrib.items():
        local = _local_name(name)
        lowered = value.lower()
        if local.startswith("on") or local in {"href", "style", "class"}:
            raise FontMakerError("INVALID_SVG", f"Unsafe or ambiguous {local} on <{kind}>")
        if "url(" in lowered or lowered.startswith(("http:", "https:", "data:", "file:")):
            raise FontMakerError("INVALID_SVG", f"External or embedded resource on <{kind}>")
    stroke = element.get("stroke")
    if stroke and stroke.lower() != "none":
        raise FontMakerError("INVALID_SVG", "Strokes must be expanded to filled paths")
    fill = element.get("fill")
    if fill and fill.lower() not in {"black", "#000", "#000000"}:
        raise FontMakerError("INVALID_SVG", "Artwork must use a solid black fill")
    if element.get("fill-rule", "nonzero").lower() != "nonzero":
        raise FontMakerError(
            "INVALID_SVG", "Even-odd fill rules must be converted to explicit contour winding"
        )
    if (
        element.get("display", "inline").lower() == "none"
        or element.get("visibility", "visible").lower() != "visible"
    ):
        raise FontMakerError("INVALID_SVG", "Hidden construction artwork is not importable")
    try:
        opacity = float(element.get("opacity", "1"))
    except ValueError as exc:
        raise FontMakerError("INVALID_SVG", "Artwork opacity must be numeric") from exc
    if opacity != 1:
        raise FontMakerError("INVALID_SVG", "Transparent artwork is not importable")


def _validate_document_security(element: Element, *, ignored: bool = False) -> None:
    kind = _local_name(element.tag)
    ignored = ignored or element.get("data-fontmaker-ignore") == "true"
    if kind in REJECTED_ELEMENTS and not (ignored and kind == "text"):
        raise FontMakerError("INVALID_SVG", f"Unsupported SVG element: <{kind}>")
    for name, value in element.attrib.items():
        local = _local_name(name)
        lowered = value.lower()
        if local.startswith("on") or local == "href":
            raise FontMakerError("INVALID_SVG", f"Unsafe {local} on <{kind}>")
        if "url(" in lowered or lowered.startswith(("http:", "https:", "data:", "file:")):
            raise FontMakerError("INVALID_SVG", f"External or embedded resource on <{kind}>")
    for child in element:
        _validate_document_security(child, ignored=ignored)


def _record_path(data: str, transform: Transform) -> RecordingPen:
    pen = RecordingPen()
    try:
        parse_path(data, TransformPen(pen, transform))
    except Exception as exc:
        raise FontMakerError("INVALID_SVG", f"Cannot parse path data: {exc}") from exc
    moves = sum(operation == "moveTo" for operation, _ in pen.value)
    closes = sum(operation == "closePath" for operation, _ in pen.value)
    ends = sum(operation == "endPath" for operation, _ in pen.value)
    if not moves or closes != moves or ends:
        raise FontMakerError("INVALID_SVG", "Every outline contour must be explicitly closed")
    return pen


def normalize_svg(source: Path, contract: SvgContract) -> NormalizedSvg:
    try:
        data = source.read_bytes()
    except OSError as exc:
        raise FontMakerError("GLYPH_SOURCE_UNREADABLE", f"Cannot read SVG: {source}") from exc
    if len(data) > MAX_SVG_BYTES:
        raise FontMakerError("SVG_TOO_LARGE", f"SVG exceeds {MAX_SVG_BYTES} bytes")
    try:
        root = SafeET.fromstring(data)
    except Exception as exc:
        raise FontMakerError("INVALID_SVG", f"Cannot parse SVG XML: {exc}") from exc
    if _local_name(root.tag) != "svg":
        raise FontMakerError("INVALID_SVG", "Root element must be <svg>")

    view_box = root.get("viewBox")
    if view_box is None:
        raise FontMakerError("INVALID_SVG", "SVG requires an explicit viewBox")
    parsed_view_box = tuple(_number_list(view_box, "viewBox"))
    if len(parsed_view_box) != 4 or any(
        abs(actual - expected) > 1e-6
        for actual, expected in zip(parsed_view_box, contract.view_box, strict=True)
    ):
        raise FontMakerError(
            "SVG_CONTRACT_MISMATCH",
            f"Expected viewBox {' '.join(f'{v:g}' for v in contract.view_box)}, got {view_box}",
        )

    _validate_document_security(root)

    glyph_groups = [
        element
        for element in root.iter()
        if _local_name(element.tag) == "g" and element.get("id") == "glyph"
    ]
    if len(glyph_groups) != 1:
        raise FontMakerError("INVALID_SVG", 'SVG must contain exactly one <g id="glyph">')

    path_data: list[str] = []
    recordings: list[RecordingPen] = []
    fixes: set[str] = {"stripped guides and non-artwork metadata"}

    def visit(element: Element, inherited: Transform) -> None:
        kind = _local_name(element.tag)
        if kind not in ALLOWED_ARTWORK:
            raise FontMakerError("INVALID_SVG", f"Unsupported artwork element: <{kind}>")
        _validate_attributes(element)
        local = _parse_transform(element.get("transform"))
        combined = inherited.transform(local)
        if element.get("transform"):
            fixes.add("flattened affine transforms")
        if kind == "g":
            for child in element:
                visit(child, combined)
            return
        raw_path = _primitive_path(element)
        if kind != "path":
            fixes.add("converted basic shapes to paths")
        recording = _record_path(raw_path, combined)
        svg_pen = SVGPathPen(None)
        recording.replay(svg_pen)
        path_data.append(svg_pen.getCommands())
        recordings.append(recording)

    visit(glyph_groups[0], Transform())
    operation_count = sum(len(recording.value) for recording in recordings)
    if operation_count > MAX_PATH_OPERATIONS:
        raise FontMakerError(
            "SVG_TOO_COMPLEX",
            f"SVG has {operation_count} operations; limit is {MAX_PATH_OPERATIONS}",
        )

    bounds_pen = BoundsPen(None)
    for recording in recordings:
        recording.replay(bounds_pen)

    output_root = Element(
        "svg",
        {
            "xmlns": SVG_NS,
            "viewBox": " ".join(f"{value:g}" for value in contract.view_box),
            "data-fontmaker-normalized": "1",
        },
    )
    output_group = SubElement(output_root, "g", {"id": "glyph", "fill": "#000000"})
    for data_item in path_data:
        SubElement(output_group, "path", {"d": data_item})
    stream = BytesIO()
    ElementTree(output_root).write(stream, encoding="utf-8", xml_declaration=True)
    return NormalizedSvg(
        content=stream.getvalue(),
        path_data=tuple(path_data),
        bounds=bounds_pen.bounds,
        operation_count=operation_count,
        fixes=tuple(sorted(fixes)),
    )


def font_space_recordings(path: Path, contract: SvgContract) -> list[RecordingPen]:
    """Read canonical SVG and return commands in the project's font coordinate system."""
    normalized = normalize_svg(path, contract)
    transform = Transform(
        contract.scale,
        0,
        0,
        -contract.scale,
        contract.translate_x * contract.scale,
        (contract.baseline_y + contract.translate_y) * contract.scale,
    )
    recordings: list[RecordingPen] = []
    for data in normalized.path_data:
        recordings.append(_record_path(data, transform))
    return recordings


def recording_to_json(recording: RecordingPen) -> list[dict[str, Any]]:
    # FontForge's foreground layer is cubic. SVG Q/T commands must be
    # degree-elevated before replay, rather than sent to its quadratic-only pen.
    cubic = RecordingPen()
    current = start = (0.0, 0.0)
    for operation, points in recording.value:
        if operation == "qCurveTo":
            for control, end in decomposeQuadraticSegment(points):
                first = tuple((current[i] + 2 * control[i]) / 3 for i in (0, 1))
                second = tuple((end[i] + 2 * control[i]) / 3 for i in (0, 1))
                cubic.curveTo(first, second, end)
                current = end
        else:
            getattr(cubic, operation)(*points)
            if operation == "moveTo":
                current = start = points[0]
            elif operation in {"lineTo", "curveTo"}:
                current = points[-1]
            elif operation == "closePath":
                current = start
    commands: list[dict[str, Any]] = []
    for operation, points in cubic.value:
        commands.append(
            {
                "op": operation,
                "points": [[round(float(x), 4), round(float(y), 4)] for x, y in points],
            }
        )
    return commands
