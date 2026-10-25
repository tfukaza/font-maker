# Latin coverage profiles and audit

Read this when selecting a coverage target or checking exported coverage. The machine-readable [inventory](latin-coverage.json) is versioned source data, not a claim that every listed glyph has been drawn.

## Provenance and discrepancies

The inventory credits [Monotype's recommendation](https://foundrysupport.monotype.com/hc/en-us/articles/360029280752-Recommended-Character-Set) and its [downloadable Unicode spreadsheet](https://foundrysupport.monotype.com/hc/en-us/article_attachments/360048897872), retrieved September 14, 2026 (America/Los_Angeles). Column A, rows 1–186, contains 186 distinct codepoints; column B supplies labels. The JSON records the attachment SHA-256 and extraction details so a later source update cannot silently change the profile.

The release baseline is the union of 103 prototype characters and those 186 codepoints: **191**, retaining ASCII U+003C, U+003E, U+005E, U+0060, and U+007E omitted by the spreadsheet. The spreadsheet omits `Â` even though the article displays it, and omits `Ž` while including `ž`. It includes several characters not apparent in the web table; see the JSON discrepancy log. Do not add or remove entries merely to match a headline or perceived symmetry. Language-specific additions such as `Â` belong in the project's explicit extension set.

This is a Latin **display baseline**, not universal Latin coverage or proof of every Western language. Neither the source recommendation nor its count certifies shaping, accent placement, visual quality, or combining-mark support.

## Audit actual exports

1. Select `prototype`, `latin_display_release`, or an explicit focused-study inventory; add any required language-specific codepoints.
2. Inspect each exported font's Unicode cmap using fontTools, not glyph names or total glyph count. Exclude mappings to `.notdef`/glyph ID 0. Compare required minus mapped codepoints, sorted numerically.
3. Report every missing item as `U+XXXX character UNICODE NAME`, plus profile and counts. A complete count with the wrong mappings is a failure. Check unexpected cmap mappings too, especially inferred presentation-form mappings on replacement glyphs.
4. Shape representative strings covering required characters with no fallback and no `.notdef`; inspect actual drawings. A mapping to an unrelated base, empty drawing, or browser fallback does not establish usable coverage. Space is intentionally blank and still needs correct width.
5. Check all export formats and matching family styles. If styles differ, identify the exact asymmetric coverage.
6. Render accents, currencies, symbols, and language-specific words. Precomposed glyphs may reuse original project bases/marks as flattened outlines. Do not claim mark positioning from precomposed coverage alone.

Example read-only audit (run with Font Maker's Python environment; substitute verified paths):

```python
import json
import unicodedata
from pathlib import Path
from fontTools.ttLib import TTFont

inventory = json.loads(Path(INVENTORY_PATH).read_text())
required = {
    int(value, 16)
    for value in inventory["profiles"]["latin_display_release"]["codepoints"]
}
with TTFont(FONT_PATH) as font:
    mapped = {
        cp for table in font["cmap"].tables if table.isUnicode()
        for cp, name in table.cmap.items()
        if name != ".notdef" and font.getGlyphID(name) != 0
    }
for cp in sorted(required - mapped):
    print(f"U+{cp:04X} {chr(cp)} {unicodedata.name(chr(cp), 'UNNAMED')}")
```

Also inspect disagreement among Unicode subtables; a union is useful for inventory but must not hide a conflicting mapping in the subtable selected by a target renderer.

## Acceptance language

A 103-character prototype is a completed **prototype**, not a Latin display release: it lacks 88 baseline codepoints. Label smaller scopes as incomplete studies. Even a full 191-codepoint result requires language-specific checks before naming supported languages. State limitations precisely rather than calling the font “full Latin.”
