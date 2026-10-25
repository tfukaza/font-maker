import shutil

import pytest
from fontTools.ttLib import TTFont

from font_maker.models import LigatureRule
from font_maker.service import FontMakerService


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge not installed")
def test_ligature_names_do_not_create_implicit_unicode(tmp_path, svg_writer):
    service = FontMakerService()
    root = tmp_path / "font"
    opened = service.create_project(str(root), "Unmapped Study")
    inputs = []
    for name, points in [("s", ["U+0073"]), ("t", ["U+0074"]), ("s_t", [])]:
        svg = svg_writer(tmp_path / (name + ".svg"), ["M50 300H450V800H50Z"])
        inputs.append(dict(name=name, codepoints=points, svg_path=str(svg), advance_width=500))
    revision = service.upsert_glyphs(opened["project_id"], opened["revision"], inputs).revision
    service.set_ligatures(
        opened["project_id"],
        revision,
        upsert=[LigatureRule(feature="dlig", sequence=["s", "t"], replacement="s_t")],
    )
    build = service.build(opened["project_id"], ["ttf", "otf", "woff2"])
    for artifact in build["artifacts"]:
        with TTFont(root / artifact["path"]) as font:
            assert font.getBestCmap() == {32: "space", 115: "s", 116: "t"}
            assert "s_t" in font.getGlyphOrder()
    shaped = service.shape(opened["project_id"], "st", {"dlig": True})
    assert [g["glyph_name"] for g in shaped["glyphs"]] == ["s_t"]
