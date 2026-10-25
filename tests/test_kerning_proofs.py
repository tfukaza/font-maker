from __future__ import annotations

import json
import runpy
import shutil
import struct
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from font_maker.models import KerningPair
from font_maker.service import FontMakerService

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills/font-spacing-kerning/scripts/render_kerning_proofs.py"
)
PROOFS = runpy.run_path(str(SCRIPT))


def test_text_splitting_preserves_boundary_pairs_and_progresses():
    text = "a abcdefghijk rare typography"
    chunks = PROOFS["split_text"](text, lambda part: len(part) <= 5)
    assert all(1 <= len(chunk) <= 5 for chunk in chunks)
    pairs = {chunk[index : index + 2] for chunk in chunks for index in range(len(chunk) - 1)}
    assert all(text[index : index + 2] in pairs for index in range(len(text) - 1))


def test_pair_matrix_is_complete_ordered_and_case_sensitive():
    sources, inventory = PROOFS["collect_sources"](
        include_defaults=False, left_chars="AAVv", right_chars="VvA"
    )
    assert [source["text"] for source in sources] == [
        "AV",
        "Av",
        "AA",
        "VV",
        "Vv",
        "VA",
        "vV",
        "vv",
        "vA",
    ]
    assert all(source["origins"] == ["matrix-forward"] for source in sources)
    assert inventory == {
        "supplied_left_chars": "AAVv",
        "supplied_right_chars": "VvA",
        "left_chars": "AVv",
        "right_chars": "VvA",
        "both_directions": False,
        "forward_pair_count": 9,
        "reverse_pair_count": 0,
        "unique_pair_count": 9,
    }


def test_reverse_matrix_keeps_asymmetric_pairs_and_deduplicates_self_pairs():
    sources, inventory = PROOFS["collect_sources"](
        include_defaults=False, left_chars="Wa", right_chars="ae", both_directions=True
    )
    assert [source["text"] for source in sources] == ["Wa", "We", "aa", "ae", "aW", "eW", "ea"]
    assert sources[2]["origins"] == ["matrix-forward", "matrix-reverse"]
    assert inventory["forward_pair_count"] == inventory["reverse_pair_count"] == 4
    assert inventory["unique_pair_count"] == 7
    forward_only, _ = PROOFS["collect_sources"](
        include_defaults=False, left_chars="W", right_chars="e"
    )
    assert [source["text"] for source in forward_only] == ["We"]


def test_duplicate_samples_retain_default_explicit_and_matrix_provenance():
    sources, _ = PROOFS["collect_sources"](
        pairs=["We", "We"], texts=["We"], left_chars="WW", right_chars="ee"
    )
    matching = [source for source in sources if source["text"] == "We"]
    assert matching == [
        {
            "group": "mixed",
            "text": "We",
            "origins": ["mixed", "custom-pair", "matrix-forward", "custom-text"],
        }
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        {"left_chars": "A"},
        {"right_chars": "V"},
        {"left_chars": "", "right_chars": "V"},
        {"left_chars": "A", "right_chars": ""},
        {"left_chars": "A V", "right_chars": "V"},
        {"left_chars": "A", "right_chars": "V\n"},
        {"left_chars": "A\x00", "right_chars": "V"},
        {"left_chars": "A", "right_chars": "V\x7f"},
        {"left_chars": "A\u200b", "right_chars": "V"},
        {"both_directions": True},
    ],
)
def test_invalid_matrix_arguments_fail_before_rendering(arguments):
    with pytest.raises(ValueError):
        PROOFS["collect_sources"](**arguments)


@pytest.mark.fontforge
@pytest.mark.skipif(shutil.which("fontforge") is None, reason="FontForge is not installed")
def test_proof_runtime_retains_shaping_and_missing_glyph_evidence(tmp_path, svg_writer):
    service = FontMakerService()
    project_path = tmp_path / "font"
    created = service.create_project(str(project_path), "Proof Fixture")
    inputs = []
    for name in dict.fromkeys("AVTypography"):
        source = svg_writer(tmp_path / f"{name}.svg", ["M50 100H450V800H50Z"])
        inputs.append(
            {
                "name": name,
                "svg_path": str(source),
                "codepoints": [f"U+{ord(name):04X}"],
                "advance_width": 600,
            }
        )
    imported = service.upsert_glyphs(created["project_id"], created["revision"], inputs)
    changed = service.set_kerning(
        created["project_id"],
        imported.revision,
        upsert_pairs=[KerningPair(left="A", right="V", value=-80)],
    )
    manifest_before = (project_path / "font.yaml").read_bytes()
    out = tmp_path / "proofs"
    index = PROOFS["render_proofs"](
        project_path,
        out=out,
        pairs=["AV"],
        texts=["AVΩ", "Typography", "AV" * 20],
        left_chars="AΩ",
        right_chars="V",
        both_directions=True,
        include_defaults=False,
    )
    assert index["revision"] == changed.revision
    assert (project_path / "font.yaml").read_bytes() == manifest_before
    assert index["counts"]["skipped"] == 3
    assert index["counts"]["pending"] == index["counts"]["cases"]
    for case in index["cases"]:
        assert case["review_status"] == "pending"
        assert case["observation"] == case["why_acceptable"] == ""
    first = index["cases"][0]
    assert first["origins"] == ["custom-pair", "matrix-forward"]
    assert index["pair_inventory"]["unique_pair_count"] == 4
    assert len([case for case in index["cases"] if case["source_text"] == "AV"]) == 1
    assert first["shaping"]["off"]["total_advance"] - first["shaping"]["on"]["total_advance"] == 80
    assert first["shaping"]["on"]["features"]["liga"] is False
    assert first["shaping"]["off"]["features"]["liga"] is False
    skipped = [case for case in index["cases"] if case["render_status"] == "skipped"]
    assert {case["text"] for case in skipped} == {"AVΩ", "ΩV", "VΩ"}
    for case in skipped:
        assert case["missing_glyphs"] == [{"character": "Ω", "codepoint": "U+03A9"}]
        assert case["review_status"] == "pending"
        assert "shaping" not in case
    typography = [case for case in index["cases"] if case["source_text"] == "Typography"]
    assert len(typography) == 1
    assert typography[0]["text"] == "Typography"
    assert typography[0]["layout"] == "full-width-stacked"
    samples = typography[0]["samples"]
    assert samples["off"]["x"] == samples["on"]["x"]
    assert samples["off"]["y"] + samples["off"]["logical_height"] < samples["on"]["y"]
    assert first["layout"] == "side-by-side"
    assert first["samples"]["off"]["y"] == first["samples"]["on"]["y"]
    assert first["samples"]["off"]["x"] < first["samples"]["on"]["x"]
    for sheet in index["sheets"]:
        svg = ET.fromstring((out / sheet["svg"]).read_bytes())
        assert struct.unpack(">II", (out / sheet["png"]).read_bytes()[16:24]) == (
            int(svg.attrib["width"]) * 3,
            int(svg.attrib["height"]) * 3,
        )
        assert int(svg.attrib["height"]) <= 650
        assert sheet["logical_width"] == int(svg.attrib["width"])
        assert sheet["logical_height"] == int(svg.attrib["height"])
        labels = [element.attrib.get("aria-label", "") for element in svg.iter()]
        assert any("KERN OFF LIGA OFF" in label for label in labels)
        assert any("KERN ON LIGA OFF" in label for label in labels)
    assert json.loads((out / "index.json").read_text())["counts"] == index["counts"]
    with pytest.raises(FileExistsError):
        PROOFS["render_proofs"](project_path, out=out, pairs=["AV"], include_defaults=False)
