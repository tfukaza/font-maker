"""Isolated FontForge compiler adapter and font artifact inspection."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

from .errors import FontMakerError
from .models import Artifact, Diagnostic, FontProject, Severity, codepoint_to_int
from .store import ProjectStore
from .svg import font_space_recordings, recording_to_json

SUPPORTED_FONTFORGE_VERSION = "20251009"


def _worker_limits(timeout: float) -> Callable[[], None] | None:
    if os.name != "posix":
        return None

    def apply_limits() -> None:
        import resource

        cpu_seconds = max(5, int(timeout) + 5)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024 * 1024, 32 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))

    return apply_limits


def find_fontforge() -> str | None:
    configured = os.environ.get("FONTMAKER_FONTFORGE")
    if configured:
        path = Path(configured).expanduser().resolve()
        return str(path) if path.is_file() else None
    return shutil.which("fontforge")


def fontforge_version(executable: str | None = None) -> str | None:
    command = executable or find_fontforge()
    if command is None:
        return None
    try:
        result = subprocess.run(
            [command, "-version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout + "\n" + result.stderr).strip()
    match = re.search(r"(?:fontforge|Version:)\s*(\d{8})", output, re.IGNORECASE)
    return match.group(1) if match else None


def require_fontforge() -> str:
    executable = find_fontforge()
    if executable is None:
        raise FontMakerError(
            "FONTFORGE_NOT_FOUND",
            "FontForge is required. Install it with `brew bundle` on macOS or set FONTMAKER_FONTFORGE.",
        )
    actual_version = fontforge_version(executable)
    if actual_version != SUPPORTED_FONTFORGE_VERSION:
        raise FontMakerError(
            "UNSUPPORTED_FONTFORGE_VERSION",
            f"Font Maker 0.1.0 requires FontForge {SUPPORTED_FONTFORGE_VERSION}.",
            actual_version=actual_version,
            executable=executable,
        )
    return executable


def _read_worker_result(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FontMakerError(
            "FONTFORGE_INVALID_RESULT", "FontForge returned an unreadable worker result."
        ) from exc
    if not isinstance(result, dict):
        raise FontMakerError(
            "FONTFORGE_INVALID_RESULT", "FontForge worker result must be a JSON object."
        )
    return result


def _tail_text(path: Path, limit: int = 4000) -> str:
    try:
        with path.open("rb") as stream:
            stream.seek(0, os.SEEK_END)
            size = stream.tell()
            stream.seek(max(0, size - limit))
            return stream.read(limit).decode("utf-8", errors="replace")
    except OSError:
        return ""


def expand_kerning_pairs(project: FontProject) -> list[dict[str, Any]]:
    pairs: dict[tuple[str, str], int] = {}

    def members(selector: str) -> list[str]:
        if selector.startswith("@"):
            return project.kerning.groups.get(selector[1:], [])
        return [selector]

    for pair in project.kerning.pairs:
        if pair.left.startswith("@") and pair.right.startswith("@"):
            continue
        for left in members(pair.left):
            for right in members(pair.right):
                if left in project.glyphs and right in project.glyphs:
                    pairs[(left, right)] = pair.value
    return [
        {"left": left, "right": right, "value": value}
        for (left, right), value in sorted(pairs.items())
    ]


def build_kerning_classes(project: FontProject) -> list[dict[str, Any]]:
    class_pairs = [
        pair
        for pair in project.kerning.pairs
        if pair.left.startswith("@") and pair.right.startswith("@")
    ]
    if not class_pairs:
        return []
    left_names = sorted({pair.left[1:] for pair in class_pairs})
    right_names = sorted({pair.right[1:] for pair in class_pairs})
    values = {(pair.left[1:], pair.right[1:]): pair.value for pair in class_pairs}
    return [
        {
            "first_classes": [project.kerning.groups[name] for name in left_names],
            "second_classes": [project.kerning.groups[name] for name in right_names],
            "offsets": [
                values.get((left_name, right_name), 0)
                for left_name in left_names
                for right_name in right_names
            ],
        }
    ]


def _serialize_glyph(store: ProjectStore, project: FontProject, name: str) -> dict[str, Any]:
    record = project.glyphs[name]
    path = store.resolve_confined(record.source, must_exist=True)
    recordings = font_space_recordings(path, project.svg)
    bounds_pen = BoundsPen(None)
    for recording in recordings:
        recording.replay(bounds_pen)
    x_shift = 0
    if bounds_pen.bounds is not None:
        x_min, _, x_max, _ = bounds_pen.bounds
        if record.left_side_bearing is not None:
            x_shift = record.left_side_bearing - x_min
        elif record.right_side_bearing is not None:
            x_shift = record.advance_width - record.right_side_bearing - x_max
    return {
        "name": name,
        "codepoints": [codepoint_to_int(value) for value in record.codepoints],
        "advance_width": record.advance_width,
        "x_shift": x_shift,
        "contours": [recording_to_json(recording) for recording in recordings],
    }


def _artifact(path: Path, revision: str, root: Path) -> Artifact:
    data = path.read_bytes()
    mime = {
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".woff2": "font/woff2",
        ".svg": "image/svg+xml",
        ".png": "image/png",
    }.get(path.suffix.lower(), "application/octet-stream")
    return Artifact(
        artifact_id=str(uuid.uuid4()),
        path=path.relative_to(root).as_posix(),
        mime_type=mime,
        size=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        revision=revision,
    )


def inspect_font(path: Path) -> dict[str, Any]:
    with TTFont(path, lazy=False) as font:
        return {
            "tables": sorted(font.keys()),
            "glyph_count": len(font.getGlyphOrder()),
            "units_per_em": font["head"].unitsPerEm,
            "has_gpos": "GPOS" in font,
            "has_gsub": "GSUB" in font,
        }


def suggest_spacing_with_fontforge(
    store: ProjectStore,
    project: FontProject,
    glyph_names: list[str],
    pair_candidates: list[tuple[str, str]],
    target_separation: int,
    *,
    timeout: float = 60,
) -> dict[str, Any]:
    executable = require_fontforge()
    driver = Path(__file__).with_name("fontforge_driver.py")
    request = {
        "operation": "suggest_spacing",
        "font": {
            **project.font.model_dump(mode="json"),
            "postscript_name": project.font.postscript_name,
        },
        "metrics": project.metrics.model_dump(mode="json"),
        "build_options": project.build.model_dump(mode="json"),
        "glyphs": [_serialize_glyph(store, project, name) for name in sorted(project.glyphs)],
        "spacing": {
            "glyph_names": glyph_names,
            "pair_candidates": pair_candidates,
            "target_separation": target_separation,
            "minimum_kerning": max(5, project.metrics.units_per_em // 100),
        },
    }
    with tempfile.TemporaryDirectory(prefix="fontmaker-spacing-") as temporary:
        temp = Path(temporary)
        request_path = temp / "request.json"
        result_path = temp / "result.json"
        stdout_path = temp / "stdout.log"
        stderr_path = temp / "stderr.log"
        request_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")
        try:
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                completed = subprocess.run(
                    [
                        executable,
                        "-lang=py",
                        "-script",
                        str(driver),
                        str(request_path),
                        str(result_path),
                    ],
                    check=False,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=timeout,
                    cwd=temp,
                    preexec_fn=_worker_limits(timeout),
                    start_new_session=True,
                )
        except subprocess.TimeoutExpired as exc:
            raise FontMakerError(
                "FONTFORGE_TIMEOUT", f"FontForge spacing exceeded {timeout:g}s"
            ) from exc
        if not result_path.is_file():
            raise FontMakerError(
                "FONTFORGE_CRASH",
                "FontForge exited without a structured spacing result",
                returncode=completed.returncode,
                stderr=_tail_text(stderr_path),
            )
        result = _read_worker_result(result_path)
        if completed.returncode or not result.get("ok"):
            raise FontMakerError(
                "FONTFORGE_ERROR",
                result.get("error", "FontForge spacing failed"),
                returncode=completed.returncode,
                stderr=_tail_text(stderr_path),
            )
        spacing = result.get("spacing")
        if not isinstance(spacing, dict):
            raise FontMakerError(
                "FONTFORGE_INVALID_RESULT",
                "FontForge returned an invalid spacing result",
            )
    return {
        **spacing,
        "fontforge_version": result.get("fontforge_version"),
    }


def build_font(
    store: ProjectStore,
    project: FontProject,
    formats: list[str] | None = None,
    *,
    timeout: float = 60,
    persist: bool = True,
) -> tuple[list[Artifact], list[Diagnostic], dict[str, Any]]:
    executable = require_fontforge()
    requested = list(dict.fromkeys(formats or project.build.formats))
    invalid = sorted(set(requested) - {"ttf", "otf", "woff2"})
    if invalid:
        raise FontMakerError("UNSUPPORTED_FORMAT", f"Unsupported format(s): {', '.join(invalid)}")
    if not project.glyphs:
        raise FontMakerError("EMPTY_FONT", "Add at least one glyph before building")

    revision = store.revision(project)
    basename = project.font.postscript_name
    output_dir = store.resolve_confined(project.build.output_dir)
    if persist:
        output_dir.mkdir(parents=True, exist_ok=True)
    driver = Path(__file__).with_name("fontforge_driver.py")

    with tempfile.TemporaryDirectory(prefix="fontmaker-build-") as temporary:
        temp = Path(temporary)
        native_formats = [value for value in requested if value in {"ttf", "otf"}]
        if "woff2" in requested and "ttf" not in native_formats:
            native_formats.append("ttf")
        outputs = {value: str(temp / f"{basename}.{value}") for value in native_formats}
        request = {
            "font": {
                **project.font.model_dump(mode="json"),
                "postscript_name": project.font.postscript_name,
            },
            "metrics": project.metrics.model_dump(mode="json"),
            "build_options": project.build.model_dump(mode="json"),
            "glyphs": [_serialize_glyph(store, project, name) for name in sorted(project.glyphs)],
            "kerning_pairs": expand_kerning_pairs(project),
            "kerning_classes": build_kerning_classes(project),
            "ligatures": [rule.model_dump(mode="json") for rule in project.ligatures],
            "outputs": outputs,
        }
        request_path = temp / "request.json"
        result_path = temp / "result.json"
        stdout_path = temp / "stdout.log"
        stderr_path = temp / "stderr.log"
        request_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")
        command = [
            executable,
            "-lang=py",
            "-script",
            str(driver),
            str(request_path),
            str(result_path),
        ]
        try:
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                completed = subprocess.run(
                    command,
                    check=False,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=timeout,
                    cwd=temp,
                    preexec_fn=_worker_limits(timeout),
                    start_new_session=True,
                )
        except subprocess.TimeoutExpired as exc:
            raise FontMakerError("FONTFORGE_TIMEOUT", f"FontForge exceeded {timeout:g}s") from exc
        if not result_path.is_file():
            raise FontMakerError(
                "FONTFORGE_CRASH",
                "FontForge exited without a structured result",
                returncode=completed.returncode,
                stderr=_tail_text(stderr_path),
            )
        result = _read_worker_result(result_path)
        if completed.returncode or not result.get("ok"):
            raise FontMakerError(
                "FONTFORGE_ERROR",
                result.get("error", "FontForge build failed"),
                returncode=completed.returncode,
                stderr=_tail_text(stderr_path),
            )

        if "woff2" in requested:
            source_ttf = Path(outputs["ttf"])
            woff_path = temp / f"{basename}.woff2"
            with TTFont(source_ttf) as font:
                font.flavor = "woff2"
                font.save(woff_path)
            outputs["woff2"] = str(woff_path)

        artifacts: list[Artifact] = []
        inspections: dict[str, Any] = {}
        for format_name in requested:
            source = Path(outputs[format_name])
            inspected_path = source
            if persist:
                destination = output_dir / source.name
                store.atomic_write(destination, source.read_bytes())
                artifacts.append(_artifact(destination, revision, store.root))
                inspected_path = destination
            inspections[format_name] = inspect_font(inspected_path)

    diagnostics: list[Diagnostic] = []
    if result.get("validation"):
        glyph_validation = result.get("glyph_validation") or {}
        if glyph_validation:
            for glyph_name, flags in sorted(glyph_validation.items()):
                diagnostics.append(
                    Diagnostic(
                        code="FONTFORGE_VALIDATION_FLAGS",
                        severity=Severity.WARNING,
                        message="FontForge reported validation flags on the generated glyph.",
                        glyph=glyph_name,
                        measurements={"bitmask": int(flags)},
                        suggested_action="Inspect and repair the affected outline.",
                    )
                )
        else:
            diagnostics.append(
                Diagnostic(
                    code="FONTFORGE_VALIDATION_FLAGS",
                    severity=Severity.WARNING,
                    message="FontForge reported validation flags on the generated font.",
                    measurements={"bitmask": int(result["validation"])},
                    suggested_action="Run validate_font_project and inspect affected outlines.",
                )
            )
    metadata = {
        "name": "FontForge",
        "fontforge_version": result.get("fontforge_version"),
        "license": "GPL-3.0-or-later",
        "credit": "FontForge by George Williams and the FontForge contributors",
        "source": "https://github.com/fontforge/fontforge/tree/20251009",
        "revision": revision,
        "inspections": inspections,
    }
    return artifacts, diagnostics, metadata
