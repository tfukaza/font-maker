# Kerning proof script contract

Use [render_kerning_proofs.py](../scripts/render_kerning_proofs.py) to generate repeatable samples, not aesthetic verdicts. Resolve its absolute path relative to this skill's directory; do not assume a repository-relative path works in an installed plugin. Run with a Python interpreter that has Font Maker and its dependencies installed.

Example (replace both absolute paths):

```shell
/path/to/fontmaker/python /path/to/font-spacing-kerning/scripts/render_kerning_proofs.py /path/to/project --pixel-scale 3 --pair ra --pair Ty --text "rare Typography parallel"
```

For a systematic inventory, choose risk characters from the actual outlines and cross them with the font's relevant encoded neighbors. This example covers `AVWTY` before and after every Latin letter, including repeated/self pairs where the sets overlap; replace or extend these sets for the font being assessed:

```shell
/path/to/fontmaker/python /path/to/font-spacing-kerning/scripts/render_kerning_proofs.py /path/to/project --no-defaults --left-chars AVWTY --right-chars ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --both-directions --text "We Welcome Wednesday"
```

To check every ordered combination within one selected set, supply the same set on both sides. `--both-directions` is redundant in that case. Review larger inventories in manageable batches and retain the indexes; generating a matrix does not inspect it.

## Options

| Argument | Behavior |
| --- | --- |
| positional project | Font project directory |
| `--out PATH` | New output directory; refuses overwrite |
| `--font-size` | Integer 8–512, default 64 |
| `--pixel-scale` | Integer 1–4, default 3 |
| `--sheet-width` | Integer 320–1200, default 640 |
| `--rows-per-sheet` | Integer 1–8, default 4 |
| `--liga on\|off` | Hold standard ligatures fixed; default off |
| `--pair TEXT` | Repeatable, exactly two characters without whitespace or controls |
| `--left-chars CHARS` | Left characters of the full Cartesian product; requires `--right-chars` |
| `--right-chars CHARS` | Right characters of the product; requires `--left-chars` |
| `--both-directions` | Add the reverse of each matrix pair; requires both character sets |
| `--text TEXT` | Repeatable nonempty single line, at most 2000 characters |
| `--no-defaults` | Use only supplied cases |

Default samples cover caps, mixed case, open forms, f contexts, punctuation, words, and sentences. They are examples, not exhaustive assurance. Add this font's risky pairs and exact target words. Output defaults to a new proof directory under the project's `build/previews`, named with a revision prefix and a random temporary-directory suffix.

Character sets must be nonempty and contain no whitespace, control, or invisible format characters. Case is preserved: `A` and `a` remain separate. Characters are deduplicated in input order, and the matrix is left-major (`AV` is distinct from `VA`); self-pairs are included. Forward cases precede any added reverse cases. Identical sample strings, including overlaps with explicit pairs and default examples, render once in first-seen order. Each case's `origins` retains all contributing groups (`matrix-forward`, `matrix-reverse`, `custom-pair`, etc.); `group` retains the first. No case is removed because its glyph is missing.

The Python `render_proofs` API accepts the corresponding `left_chars`, `right_chars`, and `both_directions` keyword arguments. `index.json` records supplied and deduplicated sets, directions, and generated pair counts under `pair_inventory`. These counts describe the requested inventory, including missing glyphs, rather than accepted coverage. With no matrix, `pair_inventory` is null.

## Actual feature settings

OFF: `{"kern": false, "liga": chosen, "rlig": true, "dlig": false}`

ON: `{"kern": true, "liga": chosen, "rlig": true, "dlig": false}`

Only kerning changes. “OFF” does **not** mean all substitutions are off. The script has no discretionary-ligature toggle and is not a ligature acceptance generator. Use `shape_text`/`preview_font` with explicit maps for ordinary/kerning-only/ligature comparisons and replacement boundaries.

Long lines are split with a one-character overlap to preserve adjacent pair coverage. This does not guarantee preservation of longer ligatures or their word context. Verify exact substrings and shaping; use focused manual previews for those sequences.

## Outputs and review

The output contains a compiled `proof-font.ttf` snapshot, PNG/SVG sheets, and `index.json` with project revision, font-byte SHA-256, source cases, shaping, dimensions, image hashes, and pending review entries. A new source revision needs fresh proofs. Generation may rebuild derived artifacts but does not change the manifest or glyph sources.

Wide rows use stacked comparisons. Missing glyphs are recorded/skipped, not accepted. `review_status` starts pending: open each actual sheet, record an observation and `why_acceptable` when justified, or an unresolved finding/action. Preserve the recorded identifiers and settings. `counts.pending` is a generation-time summary; manual case-status changes do not recalculate it. Report current reviewed totals from the case records rather than quoting that stale summary. Do not report all generated cases as inspected or accepted.

Use high-resolution sheets to diagnose, with separate native-size previews for small-text behavior. Keep the skill's 3×/4×/1× resolution distinction and split sheets that viewers shrink excessively.
