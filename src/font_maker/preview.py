"""HarfBuzz shaping and deterministic compiled-outline previews."""

from __future__ import annotations

import base64
import hashlib
import html
import shutil
import subprocess
import sysconfig
import tempfile
import uuid
from pathlib import Path
from typing import Any

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from .errors import FontMakerError
from .models import Artifact, FontProject
from .store import ProjectStore


def shape_font(
    font_path: Path,
    text: str,
    features: dict[str, bool] | None = None,
    *,
    direction: str | None = None,
    script: str | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    blob = hb.Blob.from_file_path(font_path)
    face = hb.Face(blob)
    font = hb.Font(face)
    upm = face.upem
    font.scale = (upm, upm)
    buffer = hb.Buffer()
    buffer.add_str(text)
    if direction:
        buffer.direction = direction
    if script:
        buffer.script = script
    if language:
        buffer.language = language
    if not (direction and script and language):
        buffer.guess_segment_properties()
    hb.shape(font, buffer, features or {"kern": True, "liga": True})
    glyphs = []
    for info, position in zip(buffer.glyph_infos, buffer.glyph_positions, strict=True):
        glyphs.append(
            {
                "glyph_id": info.codepoint,
                "glyph_name": font.glyph_to_string(info.codepoint),
                "cluster": info.cluster,
                "x_advance": position.x_advance,
                "y_advance": position.y_advance,
                "x_offset": position.x_offset,
                "y_offset": position.y_offset,
            }
        )
    return {
        "text": text,
        "direction": str(buffer.direction),
        "script": str(buffer.script),
        "language": str(buffer.language),
        "features": features or {"kern": True, "liga": True},
        "units_per_em": upm,
        "glyphs": glyphs,
        "total_advance": sum(item["x_advance"] for item in glyphs),
    }


def compose_preview_svg(
    font_path: Path,
    project: FontProject,
    shaping: dict[str, Any],
    *,
    font_size: int = 96,
    guides: bool = True,
) -> bytes:
    scale = font_size / project.metrics.units_per_em
    margin = max(16, int(font_size * 0.25))
    advance = max(int(shaping["total_advance"]), project.metrics.units_per_em // 2)
    width = max(1, int(advance * scale + margin * 2))
    vertical_span = project.metrics.ascender - project.metrics.descender + project.metrics.line_gap
    height = max(1, int(vertical_span * scale + margin * 2))
    baseline = margin + project.metrics.ascender * scale

    pieces = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<title>{html.escape(project.font.family_name)} preview</title>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    if guides:
        guide_values = [
            ("ascender", project.metrics.ascender, "#8b5cf6"),
            ("cap", project.metrics.cap_height, "#3b82f6"),
            ("x-height", project.metrics.x_height, "#10b981"),
            ("baseline", 0, "#ef4444"),
            ("descender", project.metrics.descender, "#f59e0b"),
        ]
        for label, value, color in guide_values:
            y = baseline - value * scale
            pieces.append(
                f'<line x1="0" x2="{width}" y1="{y:g}" y2="{y:g}" stroke="{color}" stroke-width="1" opacity="0.35"><title>{label}</title></line>'
            )

    with TTFont(font_path) as compiled:
        glyph_set = compiled.getGlyphSet()
        x_cursor = 0
        for shaped in shaping["glyphs"]:
            name = shaped["glyph_name"]
            if name not in glyph_set:
                name = compiled.getGlyphOrder()[shaped["glyph_id"]]
            pen = SVGPathPen(glyph_set)
            glyph_set[name].draw(pen)
            commands = pen.getCommands()
            x = margin + (x_cursor + shaped["x_offset"]) * scale
            y = baseline - shaped["y_offset"] * scale
            if guides:
                box_width = shaped["x_advance"] * scale
                pieces.append(
                    f'<rect x="{margin + x_cursor * scale:g}" y="{margin}" width="{box_width:g}" height="{height - margin * 2}" fill="none" stroke="#94a3b8" stroke-width="0.75" opacity="0.28"/>'
                )
            pieces.append(
                f'<path d="{html.escape(commands, quote=True)}" fill="#111827" transform="translate({x:g} {y:g}) scale({scale:g} {-scale:g})"/>'
            )
            x_cursor += shaped["x_advance"]
    pieces.append("</svg>")
    return "\n".join(pieces).encode()


def svg_to_png(svg: bytes, *, pixel_scale: int = 3) -> bytes:
    scripts_dir = Path(sysconfig.get_path("scripts"))
    executable = scripts_dir / (
        "resvg.exe" if sysconfig.get_platform().startswith("win") else "resvg"
    )
    if not executable.is_file():
        discovered = shutil.which("resvg")
        if discovered is None:
            raise FontMakerError("PREVIEW_RENDERER_NOT_FOUND", "The resvg renderer is unavailable.")
        executable = Path(discovered)

    with tempfile.TemporaryDirectory(prefix="fontmaker-preview-") as temporary:
        directory = Path(temporary)
        source = directory / "preview.svg"
        destination = directory / "preview.png"
        source.write_bytes(svg)
        try:
            completed = subprocess.run(
                [
                    str(executable),
                    "--quiet",
                    "--zoom",
                    str(pixel_scale),
                    str(source),
                    str(destination),
                ],
                check=False,
                capture_output=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise FontMakerError(
                "PREVIEW_RENDER_TIMEOUT", "resvg exceeded the 30 second limit."
            ) from exc
        if completed.returncode != 0 or not destination.is_file():
            message = completed.stderr.decode(errors="replace")[:1000].strip()
            suffix = f": {message}" if message else "."
            raise FontMakerError(
                "PREVIEW_RENDER_FAILED", f"resvg could not render the preview{suffix}"
            )
        return destination.read_bytes()


def write_preview(
    store: ProjectStore,
    project: FontProject,
    font_path: Path,
    text: str,
    features: dict[str, bool] | None = None,
    *,
    font_size: int = 96,
    pixel_scale: int = 3,
    guides: bool = True,
) -> tuple[list[Artifact], dict[str, Any], bytes]:
    shaping = shape_font(font_path, text, features)
    svg = compose_preview_svg(font_path, project, shaping, font_size=font_size, guides=guides)
    png = svg_to_png(svg, pixel_scale=pixel_scale)
    preview_dir = store.root / "build" / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(
        store.revision(project).encode()
        + text.encode()
        + str(features).encode()
        + str(font_size).encode()
        + str(pixel_scale).encode()
        + str(guides).encode()
    ).hexdigest()[:12]
    base = f"preview-{digest}"
    svg_path = preview_dir / f"{base}.svg"
    png_path = preview_dir / f"{base}.png"
    store.atomic_write(svg_path, svg)
    store.atomic_write(png_path, png)
    revision = store.revision(project)

    def artifact(path: Path, mime: str) -> Artifact:
        data = path.read_bytes()
        return Artifact(
            artifact_id=str(uuid.uuid4()),
            path=path.relative_to(store.root).as_posix(),
            mime_type=mime,
            size=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            revision=revision,
        )

    return [artifact(svg_path, "image/svg+xml"), artifact(png_path, "image/png")], shaping, png


def png_data_uri(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode()
