"""Exercise the shipped fonts, plus a fresh build with overlapping ligature rules."""

import runpy
import shutil
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

from font_maker.models import LigatureRule
from font_maker.preview import shape_font
from font_maker.service import FontMakerService

ROOT = Path(__file__).parents[1]
DESIGN = runpy.run_path(str(ROOT / "examples/add_super_pixel_ligatures.py"))
CODING = DESIGN["CODING"]
EXPRESSIONS = DESIGN["EXPRESSIONS"]
NAME = DESIGN["glyph_name"]
OFF = {"kern": True, "liga": False, "rlig": False, "dlig": False}
ON = {**OFF, "liga": True, "dlig": True}


@pytest.fixture(params=[(family, extension) for family in ("Fluid", "Bitmap")
                        for extension in ("ttf", "otf", "woff", "woff2")])
def font_path(request, tmp_path):
    family, extension = request.param
    path = ROOT / f"fonts/super-pixel-{family.lower()}/build/fonts/SuperPixel{family}-Regular.{extension}"
    # HarfBuzz consumes sfnt bytes; decompress web fonts before shaping them.
    with TTFont(path) as font:
        assert len(font.getBestCmap()) == 103
        assert not any(name.startswith("code_") for name in font.getBestCmap().values())
        assert font['head'].fontRevision == pytest.approx(1.001, abs=0.00002)
        assert {"DFLT", "latn"} <= {record.ScriptTag for record in font["GSUB"].table.ScriptList.ScriptRecord}
        if extension in {"woff", "woff2"}:
            path = tmp_path / "decompressed.ttf"
            font.flavor = None
            font.save(path)
    return path


def names(shaped):
    return [glyph["glyph_name"] for glyph in shaped["glyphs"]]


def test_exported_sequences_features_clusters_and_widths(font_path):
    with TTFont(font_path) as font:
        cmap = font.getBestCmap()
    for sequence in CODING + EXPRESSIONS:
        repeated = f"{sequence} {sequence}"
        for text in (sequence, f"a{sequence}b", f"({sequence})", repeated):
            off = shape_font(font_path, text, OFF)
            on = shape_font(font_path, text, ON)
            assert names(off) == [cmap[ord(char)] for char in text]
            assert names(on).count(NAME(sequence)) == (2 if text == repeated else 1)
            assert on["total_advance"] == off["total_advance"], (text, font_path)
        alone = shape_font(font_path, sequence, ON)
        assert names(alone) == [NAME(sequence)]
        assert alone["glyphs"][0]["cluster"] == 0
        defaults = shape_font(font_path, sequence)
        assert names(defaults) == ([NAME(sequence)] if sequence in CODING else [cmap[ord(c)] for c in sequence])
        # The feature tags remain independently switchable.
        for feature in ("liga", "dlig"):
            expected = feature == ("liga" if sequence in CODING else "dlig")
            shaped = shape_font(font_path, sequence, {**OFF, feature: True})
            assert (NAME(sequence) in names(shaped)) == expected


def test_overlap_boundaries_and_unrelated_text(font_path):
    cases = {
        "!==!=": ["!==", "!="], "====": ["===", "="],
        "....": ["...", "."], "<=>->": ["<=>", "->"],
        "<-><-": ["<->", "<-"], ":-):-P": [":-)", ":-P"],
    }
    with TTFont(font_path) as font:
        cmap = font.getBestCmap()
    for text, tokens in cases.items():
        expected = [NAME(token) if len(token) > 1 else cmap[ord(token)] for token in tokens]
        assert names(shape_font(font_path, text, ON)) == expected
    for text in ("T..", "V...", "F...", "r..", ":PA", ":-PA"):
        assert shape_font(font_path, text, ON)["total_advance"] == shape_font(font_path, text, OFF)["total_advance"]
    for text in ("Hello world 0123456789", "a + b / c;", "- > ! = = : )", "AVATAR office"):
        assert shape_font(font_path, text, ON)["glyphs"] == shape_font(font_path, text, OFF)["glyphs"]


def test_both_projects_share_cells_and_preserve_bitmap_geometry():
    from font_maker.store import ProjectStore

    projects = []
    for family in ("fluid", "bitmap"):
        root = ROOT / f"fonts/super-pixel-{family}"
        project = ProjectStore(root).load()
        projects.append((root, project))
    for sequence in CODING + EXPRESSIONS:
        name = NAME(sequence)
        cells = []
        for root, project in projects:
            record = project.glyphs[name]
            assert record.codepoints == []
            pen = DESIGN["outline"](root / record.source)
            cells.append(DESIGN["occupied_cells"](pen))
            if "bitmap" in root.name:
                assert all(operation in {"moveTo", "lineTo", "closePath"} for operation, _ in pen.value)
                for _, points in pen.value:
                    assert all((x - 50) % 100 == 0 and (y - 100) % 100 == 0 for x, y in points)
        assert cells[0] == cells[1]


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge not installed")
def test_fresh_build_orders_overlaps_and_supports_default_script(tmp_path, svg_writer):
    service = FontMakerService()
    root = tmp_path / "font"
    opened = service.create_project(str(root), "Symbol ligature fixture")
    source = svg_writer(tmp_path / "shape.svg", ["M50 300H350V800H50Z"])
    revision = service.upsert_glyphs(opened["project_id"], opened["revision"], [
        dict(name=name, codepoints=points, svg_path=str(source), advance_width=advance)
        for name, points, advance in [("exclam", ["U+0021"], 400), ("equal", ["U+003D"], 400),
                                      ("not_equal", [], 800), ("strict_not_equal", [], 1200)]
    ]).revision
    # Intentionally supply the shorter prefix first.
    service.set_ligatures(opened["project_id"], revision, [
        LigatureRule(sequence=["exclam", "equal"], replacement="not_equal"),
        LigatureRule(sequence=["exclam", "equal", "equal"], replacement="strict_not_equal"),
    ])
    service.build(opened["project_id"], ["ttf"])
    font = next((root / "build/fonts").glob("*.ttf"))
    for script in (None, "Zyyy", "Latn"):
        assert names(shape_font(font, "!==!=", script=script)) == ["strict_not_equal", "not_equal"]
