"""Offline contract tests for the skill's source inventory and documented cmap audit."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).parents[1]
REFERENCE = ROOT / "skills/font-production-workflow/references"
INVENTORY = REFERENCE / "latin-coverage.json"


def profile(name: str) -> set[int]:
    data = json.loads(INVENTORY.read_text())
    return {int(value, 16) for value in data["profiles"][name]["codepoints"]}


def test_inventory_is_valid_and_matches_verified_source() -> None:
    data = json.loads(INVENTORY.read_text())
    assert data["schema_version"] == 1
    source = data["source"]
    date.fromisoformat(source["retrieved_on"])
    assert source["attribution"] and source["extraction"] and data["discrepancies"]
    assert source["article_url"].startswith("https://foundrysupport.monotype.com/")
    assert source["download_url"].endswith("/360048897872")
    assert source["sha256"] == ("59368364cc40698b9b8332a276f28cc09d95e8298f68f2f604f1181cffba0c54")
    assert source["spreadsheet_rows"] == source["unique_codepoints"] == 186
    assert source["duplicate_codepoints"] == []
    for item in data["profiles"].values():
        values = item["codepoints"]
        assert all(re.fullmatch(r"[0-9A-F]{4,6}", value) for value in values)
        numbers = [int(value, 16) for value in values]
        assert numbers == sorted(set(numbers))
        assert len(numbers) == item["count"]
        assert all(0 <= cp <= 0x10FFFF and not 0xD800 <= cp <= 0xDFFF for cp in numbers)
    # Independent digest of the verified XLSX column, not a second handwritten list.
    source_values = data["profiles"]["monotype_recommended"]["codepoints"]
    assert hashlib.sha256("\n".join(source_values).encode()).hexdigest() == (
        "0e0abee42546def6d7671aef3e72ca025f5e812154cca74399b1305dd5f2c633"
    )


def test_release_preserves_prototype_and_documents_source_gaps() -> None:
    prototype = profile("prototype")
    monotype = profile("monotype_recommended")
    release = profile("latin_display_release")
    assert prototype == set(range(0x20, 0x7F)) | {
        0x2013,
        0x2014,
        0x2018,
        0x2019,
        0x201C,
        0x201D,
        0x2022,
        0x2026,
    }
    assert len(prototype) == 103
    assert release == prototype | monotype
    assert len(release) == 191
    assert prototype - monotype == {0x3C, 0x3E, 0x5E, 0x60, 0x7E}
    assert 0x00C2 not in monotype  # Â is in article text, absent from XLSX.
    assert 0x017D not in monotype and 0x017E in monotype
    assert {0x00C1, 0x00DA, 0x00B7, 0x2030} <= monotype


def exported_fixture(path: Path, codepoints: set[int], *, notdef: int | None = None) -> None:
    """Original diagnostic rectangles, not a designed font or borrowed outlines."""
    builder = FontBuilder(1000, isTTF=True)
    names = {cp: f"uni{cp:04X}" for cp in sorted(codepoints)}
    order = [".notdef", *names.values(), "unmapped_ligature"]
    builder.setupGlyphOrder(order)
    cmap = dict(names)
    if notdef is not None:
        cmap[notdef] = ".notdef"
    builder.setupCharacterMap(cmap)
    glyphs = {}
    for name in order:
        pen = TTGlyphPen(None)
        if name != "uni0020":
            pen.moveTo((50, 0))
            pen.lineTo((450, 0))
            pen.lineTo((450, 700))
            pen.lineTo((50, 700))
            pen.closePath()
        glyphs[name] = pen.glyph()
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics({name: (500, 50) for name in order})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
    builder.setupNameTable({"familyName": "Original Coverage Fixture", "styleName": "Regular"})
    builder.setupPost()
    builder.save(path)


def run_documented_audit(font_path: Path) -> None:
    body = (REFERENCE / "latin-coverage.md").read_text()
    snippet = re.search(r"```python\n(.*?)\n```", body, re.DOTALL)
    assert snippet
    exec(
        compile(snippet.group(1), "latin-coverage.md", "exec"),
        {"INVENTORY_PATH": str(INVENTORY), "FONT_PATH": str(font_path)},
    )


def test_prototype_export_cannot_pass_release(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    font = tmp_path / "prototype.ttf"
    exported_fixture(font, profile("prototype"))
    run_documented_audit(font)
    lines = capsys.readouterr().out.splitlines()
    actual_missing = {int(line.split()[0][2:], 16) for line in lines}
    assert actual_missing == profile("latin_display_release") - profile("prototype")
    assert len(lines) == 88
    assert "U+00C4 Ä LATIN CAPITAL LETTER A WITH DIAERESIS" in lines
    assert "U+20AC € EURO SIGN" in lines


def test_audit_reports_exact_accents_currencies_and_excludes_notdef(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    font = tmp_path / "missing.ttf"
    exported_fixture(
        font, profile("latin_display_release") - {0x00C4, 0x00A3, 0x20AC}, notdef=0x20AC
    )
    run_documented_audit(font)
    assert capsys.readouterr().out.splitlines() == [
        "U+00A3 £ POUND SIGN",
        "U+00C4 Ä LATIN CAPITAL LETTER A WITH DIAERESIS",
        "U+20AC € EURO SIGN",
    ]


def test_complete_inventory_has_no_missing_codepoints(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    font = tmp_path / "complete.ttf"
    exported_fixture(font, profile("latin_display_release"))
    run_documented_audit(font)
    assert capsys.readouterr().out == ""  # Only coverage passes, not design/language QA.
