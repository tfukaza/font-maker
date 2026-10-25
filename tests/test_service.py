from __future__ import annotations

import shutil
import struct
from xml.etree import ElementTree

import pytest
from fontTools.ttLib import TTFont

from font_maker.errors import RevisionConflict
from font_maker.models import KerningPair, LigatureRule
from font_maker.service import FontMakerService


def _create_fixture_project(tmp_path, svg_writer):
    service = FontMakerService()
    project_dir = tmp_path / "fixture-font"
    created = service.create_project(str(project_dir), "Fixture Sans")
    glyphs = {
        "A": ("U+0041", "M80 800L300 100L520 800L430 800L365 590L235 590L170 800Z"),
        "V": ("U+0056", "M80 100L300 800L520 100L430 100L300 590L170 100Z"),
        "f": (
            "U+0066",
            "M160 800L160 300L100 300L100 220L160 220L160 160L250 100L250 220L340 220L340 300L250 300L250 800Z",
        ),
        "i": ("U+0069", "M120 350L220 350L220 800L120 800ZM120 180L220 180L220 280L120 280Z"),
        "f_i": (
            None,
            "M100 800L100 300L50 300L50 220L100 220L100 150L190 100L190 220L300 220L300 800L210 800L210 300L190 300L190 800ZM210 100L300 100L300 190L210 190Z",
        ),
        "H": (
            "U+0048",
            "M80 100L170 100L170 405L430 405L430 100L520 100L520 800L430 800L430 495L170 495L170 800L80 800Z",
        ),
        "O": (
            "U+004F",
            "M70 450C70 220 160 90 300 90C440 90 530 220 530 450C530 680 440 810 300 810C160 810 70 680 70 450ZM165 450C165 620 210 720 300 720C390 720 435 620 435 450C435 280 390 180 300 180C210 180 165 280 165 450Z",
        ),
        "n": (
            "U+006E",
            "M80 800L80 300L165 300L165 365C205 310 265 285 325 285C440 285 500 360 500 500L500 800L410 800L410 510C410 415 380 370 315 370C230 370 170 435 170 545L170 800Z",
        ),
        "o": (
            "U+006F",
            "M70 550C70 380 160 285 300 285C440 285 530 380 530 550C530 720 440 815 300 815C160 815 70 720 70 550ZM165 550C165 670 205 730 300 730C395 730 435 670 435 550C435 430 395 370 300 370C205 370 165 430 165 550Z",
        ),
        "space": ("U+0020", None),
    }
    inputs = []
    for name, (codepoint, data) in glyphs.items():
        source = svg_writer(tmp_path / f"{name}.svg", [] if data is None else [data])
        inputs.append(
            {
                "name": name,
                "svg_path": str(source),
                "codepoints": [] if codepoint is None else [codepoint],
                "advance_width": (
                    250 if name == "space" else 600 if name not in {"f", "i", "f_i"} else 400
                ),
            }
        )
    imported = service.upsert_glyphs(created["project_id"], created["revision"], inputs)
    return service, created["project_id"], imported.revision, project_dir


def test_import_suggest_apply_and_stale_revision(tmp_path, svg_writer, monkeypatch):
    service, project_id, revision, project_dir = _create_fixture_project(tmp_path, svg_writer)
    monkeypatch.setattr(
        "font_maker.service.suggest_spacing_with_fontforge",
        lambda store, project, glyph_names, pair_candidates, target_separation: {
            "glyph_metrics": {
                name: {
                    "advance_width": 500,
                    "left_side_bearing": 30,
                    "right_side_bearing": 30,
                }
                for name in glyph_names
            },
            "kerning_pairs": [],
            "fontforge_version": "test",
        },
    )
    proposal = service.suggest_spacing(project_id, glyph_names=["A", "V"])

    assert proposal.base_revision == revision
    assert proposal.changes
    applied = service.apply_spacing_proposal(project_id, revision, proposal.proposal_id)
    assert applied.revision != revision

    with pytest.raises(RevisionConflict):
        service.apply_spacing_proposal(project_id, revision, proposal.proposal_id)

    restarted = FontMakerService()
    reopened = restarted.open_project(str(project_dir))
    assert reopened["project_id"] == project_id
    assert reopened["revision"] == applied.revision


def test_validation_rejects_overdetermined_inconsistent_glyph_metrics(tmp_path, svg_writer):
    service, project_id, revision, _ = _create_fixture_project(tmp_path, svg_writer)
    updated = service.set_glyph_metrics(
        project_id,
        revision,
        [
            {
                "name": "A",
                "advance_width": 600,
                "left_side_bearing": 10,
                "right_side_bearing": 10,
            }
        ],
    )

    diagnostics = service.validate(project_id)

    assert updated.revision != revision
    assert "INCONSISTENT_GLYPH_METRICS" in {item.code for item in diagnostics}


def test_spacing_reconciles_compiler_rounding_with_source_bounds(tmp_path, svg_writer, monkeypatch):
    service = FontMakerService()
    created = service.create_project(str(tmp_path / "fractional"), "Fractional")
    source = svg_writer(tmp_path / "o.svg", ["M20.1 300H440.9V800H20.1Z"])
    imported = service.upsert_glyphs(
        created["project_id"], created["revision"],
        [{"name": "o", "svg_path": str(source), "codepoints": ["U+006F"]}],
    )
    monkeypatch.setattr(
        "font_maker.service.suggest_spacing_with_fontforge",
        lambda *args: {
            "glyph_metrics": {"o": {
                "advance_width": 459, "left_side_bearing": 19, "right_side_bearing": 20,
            }},
            "kerning_pairs": [], "fontforge_version": "test",
        },
    )
    proposal = service.suggest_spacing(
        created["project_id"], glyph_names=["o"], target_separation=35,
    )
    assert proposal.changes[0].after == {
        "advance_width": 460, "left_side_bearing": 19, "right_side_bearing": 20,
    }
    assert len(proposal.changes[0].evidence) == 2
    service.apply_spacing_proposal(created["project_id"], imported.revision, proposal.proposal_id)
    assert not any(d.code == "INCONSISTENT_GLYPH_METRICS" for d in service.validate(created["project_id"]))


def test_uppercase_and_lowercase_sources_are_portably_distinct(tmp_path, svg_writer):
    service = FontMakerService()
    created = service.create_project(str(tmp_path / "case-safe"), "Case Safe")
    upper = svg_writer(tmp_path / "upper-source.svg", ["M100 100H300V700H100Z"])
    lower = svg_writer(tmp_path / "lower-source.svg", ["M350 300H500V700H350Z"])

    service.upsert_glyphs(
        created["project_id"],
        created["revision"],
        [
            {"name": "A", "svg_path": str(upper), "codepoints": ["U+0041"]},
            {"name": "a", "svg_path": str(lower), "codepoints": ["U+0061"]},
        ],
    )
    project = service.get_project(created["project_id"])["project"]
    upper_source = project["glyphs"]["A"]["source"]
    lower_source = project["glyphs"]["a"]["source"]

    assert upper_source.casefold() != lower_source.casefold()
    assert (tmp_path / "case-safe" / upper_source).read_bytes() != (
        tmp_path / "case-safe" / lower_source
    ).read_bytes()


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge is not installed")
def test_quadratic_svg_builds_in_cubic_fontforge_layer(tmp_path, svg_writer):
    from fontTools.pens.boundsPen import BoundsPen

    service = FontMakerService()
    created = service.create_project(str(tmp_path / "quadratic"), "Quadratic")
    source = svg_writer(tmp_path / "q-source.svg", ["M100 800Q200 0 300 800T500 800Z"])
    service.upsert_glyphs(
        created["project_id"], created["revision"],
        [{"name": "q", "svg_path": str(source), "codepoints": ["U+0071"]}],
    )
    built = service.build(created["project_id"], ["ttf", "otf", "woff2"])
    for artifact in built["artifacts"]:
        with TTFont(tmp_path / "quadratic" / artifact["path"]) as compiled:
            glyphs = compiled.getGlyphSet()
            pen = BoundsPen(glyphs)
            glyphs["q"].draw(pen)
            assert pen.bounds == pytest.approx((100, -400, 500, 400), abs=1)


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge is not installed")
@pytest.mark.parametrize("descender", [-270, -150])
def test_export_preserves_upm_when_line_metrics_span_differs(tmp_path, svg_writer, descender):
    from font_maker.models import VerticalMetrics

    service, project_id, revision, project_dir = _create_fixture_project(tmp_path, svg_writer)
    service.set_font_metrics(project_id, revision, VerticalMetrics(descender=descender))
    built = service.build(project_id, ["ttf", "otf", "woff2"])
    for artifact in built["artifacts"]:
        with TTFont(project_dir / artifact["path"]) as compiled:
            assert compiled["head"].unitsPerEm == 1000
            assert compiled["hhea"].ascent == 800
            assert compiled["hhea"].descent == descender
            assert compiled["OS/2"].sTypoDescender == descender
            assert compiled["hmtx"]["A"][0] == 600
            from fontTools.pens.boundsPen import BoundsPen

            glyphs = compiled.getGlyphSet()
            pen = BoundsPen(glyphs)
            glyphs["A"].draw(pen)
            assert pen.bounds == (80, 0, 520, 700)


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge is not installed")
def test_fontforge_build_shape_and_preview(tmp_path, svg_writer):
    service, project_id, revision, project_dir = _create_fixture_project(tmp_path, svg_writer)
    kerned = service.set_kerning(
        project_id,
        revision,
        groups={"A-left": ["A"], "V-right": ["V"]},
        upsert_pairs=[KerningPair(left="@A-left", right="@V-right", value=-80)],
    )
    ligatured = service.set_ligatures(
        project_id,
        kerned.revision,
        [LigatureRule(feature="liga", sequence=["f", "i"], replacement="f_i")],
    )

    proposal = service.suggest_spacing(
        project_id,
        glyph_names=["H", "O", "n", "o"],
        pair_candidates=[("A", "V")],
    )
    assert proposal.base_revision == ligatured.revision
    assert proposal.changes
    assert proposal.diagnostics[0].code == "FONTFORGE_SPACING_HEURISTIC"
    assert all(change.evidence for change in proposal.changes)

    assert not list((project_dir / "build" / "fonts").iterdir())
    service.validate(project_id, temporary_build=True)
    assert not list((project_dir / "build" / "fonts").iterdir())

    built = service.build(project_id, ["ttf", "otf", "woff2"])
    assert {item["mime_type"] for item in built["artifacts"]} == {
        "font/ttf",
        "font/otf",
        "font/woff2",
    }
    assert all((project_dir / item["path"]).is_file() for item in built["artifacts"])
    ttf_artifact = next(item for item in built["artifacts"] if item["mime_type"] == "font/ttf")
    with TTFont(project_dir / ttf_artifact["path"]) as compiled:
        assert compiled["head"].unitsPerEm == 1000
        assert compiled["hhea"].ascent == 800
        assert compiled["hhea"].descent == -200
        assert compiled["OS/2"].sCapHeight == 700
        assert compiled["OS/2"].sxHeight == 500
        pair_subtables = [
            subtable
            for lookup in compiled["GPOS"].table.LookupList.Lookup
            if lookup.LookupType == 2
            for subtable in lookup.SubTable
        ]
        assert any(subtable.Format == 2 for subtable in pair_subtables)

    kern_on = service.shape(project_id, "AV", {"kern": True, "liga": True})
    kern_off = service.shape(project_id, "AV", {"kern": False, "liga": True})
    assert kern_on["total_advance"] == kern_off["total_advance"] - 80
    shaped_ligature = service.shape(project_id, "fi", {"kern": True, "liga": True})
    assert [item["glyph_name"] for item in shaped_ligature["glyphs"]] == ["f_i"]

    preview, png = service.preview(project_id, "AV fi")
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(png) > 1_000
    width, height = struct.unpack(">II", png[16:24])
    svg_artifact = next(
        item for item in preview["artifacts"] if item["mime_type"] == "image/svg+xml"
    )
    svg_root = ElementTree.parse(project_dir / svg_artifact["path"]).getroot()
    assert width == int(svg_root.attrib["width"]) * 3
    assert height == int(svg_root.attrib["height"]) * 3
    assert preview["settings"]["pixel_scale"] == 3
    assert {item["mime_type"] for item in preview["artifacts"]} == {
        "image/svg+xml",
        "image/png",
    }
    assert ligatured.revision == built["revision"]
    assert built["backend"]["license"] == "GPL-3.0-or-later"
    assert len(service.get_project(project_id)["artifacts"]) >= 5
