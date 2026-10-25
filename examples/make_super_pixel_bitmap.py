"""Derive Super Pixel Bitmap: Super Pixel with square pixels and no fillets or necks."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

from font_maker.service import FontMakerService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from examples.generate_concept_fonts import _filleted_grid_loop, _grid_boundary_loops

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "super-pixel"
DEST = ROOT / "super-pixel-bitmap"
SVG = "{http://www.w3.org/2000/svg}"
# Super Pixel cells are 100 units square, with column 0 at x=50 and row 0 at y=100.
CELL, ORIGIN_X, ORIGIN_Y = 100, 50, 100


def outline(svg_path: Path) -> RecordingPen:
    pen = RecordingPen()
    root = ET.parse(svg_path).getroot()
    for path in root.iter(SVG + "path"):
        parse_path(path.attrib["d"], pen)
    return pen


def area(pen: RecordingPen) -> float:
    area_pen = AreaPen()
    pen.replay(area_pen)
    return abs(area_pen.value)


def occupied_cells(pen: RecordingPen) -> set[tuple[int, int]]:
    """Sample each cell centre; fillets and necks never reach a centre."""

    cells = set()
    for column in range(-2, 40):
        for row in range(-2, 14):
            inside = PointInsidePen(
                None,
                (ORIGIN_X + column * CELL + CELL / 2, ORIGIN_Y + row * CELL + CELL / 2),
            )
            pen.replay(inside)
            if inside.getResult():
                cells.add((column, row))
    return cells


def square_loop(points: list[tuple[float, float]]) -> str:
    return "M" + "L".join(f"{x:g} {y:g}" for x, y in points) + "Z"


def main() -> None:
    DEST.mkdir()  # Refuse to overwrite an earlier build.
    service = FontMakerService()
    original = service.open_project(str(SOURCE))
    shutil.copytree(SOURCE, DEST, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
        "build", ".fontmaker", "REVIEW.md"
    ))
    clone_service = FontMakerService()
    opened = clone_service.open_project(str(DEST))
    store, project = clone_service._store_project(opened["project_id"])
    project.project_id = str(uuid.uuid4())
    project.font.family_name = "Super Pixel Bitmap"
    store.save(project, opened["revision"])

    service = FontMakerService()
    opened = service.open_project(str(DEST))
    pid, revision = opened["project_id"], opened["revision"]
    _, project = service._store_project(pid)
    checks = {}
    with tempfile.TemporaryDirectory(prefix="super-pixel-bitmap-") as temporary:
        inputs = []
        for name, record in project.glyphs.items():
            pen = outline(DEST / record.source)
            cells = occupied_cells(pen)
            loops = _grid_boundary_loops(cells) if cells else []
            # Redrawing with the original fillets must reproduce the source, which
            # proves the sampled cells are exactly Super Pixel's pixels.
            filleted = "".join(_filleted_grid_loop(loop) for loop in loops)
            rebuilt = RecordingPen()
            if filleted:
                parse_path(filleted, rebuilt)
            assert abs(area(rebuilt) - area(pen)) < 0.5, name
            path_data = "".join(square_loop(loop) for loop in loops)
            art = f'<path d="{path_data}"/>' if path_data else ""
            # Hash the name: "A.svg" and "a.svg" collide on case-insensitive disks.
            source_id = hashlib.sha256(name.encode("utf-8")).hexdigest()
            target = Path(temporary) / f"{source_id}.svg"
            target.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">'
                f'<g id="glyph" fill="#000000">{art}</g></svg>',
                encoding="utf-8",
            )
            if path_data:
                squared = RecordingPen()
                parse_path(path_data, squared)
                assert abs(area(squared) - len(cells) * CELL * CELL) < 0.5, name
            checks[name] = cells
            inputs.append(
                dict(
                    name=name,
                    svg_path=str(target),
                    codepoints=record.codepoints,
                    advance_width=record.advance_width,
                    left_side_bearing=record.left_side_bearing,
                    right_side_bearing=record.right_side_bearing,
                )
            )
        revision = service.upsert_glyphs(pid, revision, inputs).revision
    _, project = service._store_project(pid)
    for name, record in project.glyphs.items():
        assert occupied_cells(outline(DEST / record.source)) == checks[name], name

    diagnostics = [d.model_dump(mode="json") for d in service.validate(pid, temporary_build=True)]
    assert not any(d["severity"] == "error" for d in diagnostics), diagnostics
    build = service.build(pid, ["ttf", "otf", "woff2"])
    fonts = DEST / "build" / "fonts"
    with TTFont(fonts / "SuperPixelBitmap-Regular.ttf") as font:
        assert len(font.getBestCmap()) == 103
        font.flavor = "woff"
        font.save(fonts / "SuperPixelBitmap-Regular.woff")
    previews = DEST / "build" / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    for label, text in [
        ("pangram", "The quick brown fox jumps over the lazy dog"),
        ("figures", "0123456789 !?&@#$%"),
        ("diagonals", "AVWXYZ kvwxyz /\\<>"),
    ]:
        _, png = service.preview(pid, text, font_size=72, pixel_scale=2, guides=False)
        (previews / f"{label}.png").write_bytes(png)
    assert FontMakerService().open_project(str(SOURCE))["revision"] == original["revision"]
    report = dict(
        source=original,
        revision=revision,
        cells={name: len(cells) for name, cells in checks.items()},
        diagnostics=diagnostics,
        build=build,
    )
    (DEST / "build" / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(DEST)


if __name__ == "__main__":
    main()
