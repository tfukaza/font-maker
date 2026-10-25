"""Keep the original Super Pixel dotted bodies aligned after regeneration."""

import runpy
import shutil
from pathlib import Path

import pytest
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from font_maker.service import FontMakerService

GENERATOR = runpy.run_path(
    str(Path(__file__).parents[1] / "examples/generate_concept_fonts.py")
)


def contour_bounds(glyph, glyph_set):
    recording = RecordingPen()
    glyph.draw(recording)
    contours = []
    pen = BoundsPen(glyph_set)
    for operation, points in recording.value:
        getattr(pen, operation)(*points)
        if operation in {"closePath", "endPath"}:
            contours.append(pen.bounds)
            pen = BoundsPen(glyph_set)
    return sorted(contours, key=lambda bounds: bounds[1])


def test_grid_pattern_correction_is_scoped_to_dotted_letters():
    original = GENERATOR["all_patterns"]()
    grid = GENERATOR["all_patterns"]("grid")
    assert {name for name in grid if grid[name] != original[name]} == {"i", "j"}
    assert GENERATOR["all_patterns"]("flow") == original
    for name in ("i", "j"):
        # Dot on the top cap row, one empty row, then lowercase body.
        assert "#" in grid[name][0]
        assert "#" not in grid[name][1]
        assert "#" in grid[name][2]
        assert grid[name][3:] == original[name][3:]


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge not installed")
def test_exported_dotted_bodies_follow_x_height_in_every_format(tmp_path):
    service = FontMakerService()
    root = tmp_path / "font"
    opened = service.create_project(str(root), "Super Pixel Metrics Fixture")
    patterns = GENERATOR["all_patterns"]("grid")
    inputs = []
    for name in ("i", "j", "n", "x"):
        source = tmp_path / f"glyph-U{ord(name):04X}.svg"
        advance = GENERATOR["write_svg"](source, patterns[name], "grid", name)
        inputs.append(
            dict(name=name, codepoints=[f"U+{ord(name):04X}"], svg_path=str(source), advance_width=advance)
        )
    service.upsert_glyphs(opened["project_id"], opened["revision"], inputs)
    build = service.build(opened["project_id"], ["ttf", "otf", "woff2"])
    for artifact in build["artifacts"]:
        with TTFont(root / artifact["path"]) as font:
            assert font["OS/2"].sxHeight == 500
            glyphs = font.getGlyphSet()
            for name, bottom, x_min, x_max, advance in [
                ("i", 0, 50, 150, 200),
                ("j", -100, 350, 450, 500),
            ]:
                body, dot = contour_bounds(glyphs[name], glyphs)
                assert body[1] == bottom
                assert body[3] == 500
                assert dot == (x_min, 600, x_max, 700)
                assert dot[1] - body[3] == 100
                assert font["hmtx"][name][0] == advance
            for name in ("n", "x"):
                bounds = BoundsPen(glyphs)
                glyphs[name].draw(bounds)
                assert bounds.bounds[1] == 0
                assert bounds.bounds[3] == 500
