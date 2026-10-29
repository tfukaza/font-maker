---
name: font-spacing-kerning
description: Establish base sidebearings, word separation, and kerning exceptions; review spacing proposals and justify optical judgments with compiled evidence. Use after core proportions are stable, including punctuation and substituted-glyph boundaries, and whenever a ligature replacement is added or redrawn; route shape changes to outline or ligature design.
---

# Font Spacing and Kerning

Make base spacing coherent before pair exceptions. Read the current project revision and UPM; canvas width is not advance width. Judge actual compiled images, not equal numbers or collision-free bounds.

## Establish base rhythm and word boundaries

Start with `H O` for capitals and `n o` for lowercase. Render repeated/interleaved controls with kerning disabled; use the [test corpus](../font-specimen-review/references/test-corpus.md) for starting strings. Flat, round, diagonal, and open forms need related perceived texture, not identical bearings. Preserve intentional asymmetry.

When a gap follows one glyph across many neighbors, fix its bearings or construction before adding exceptions. Compare internal gaps with **word spaces** in real sentences: readers should distinguish words immediately without turning every space into a hole. If the whole design is widely spaced, a numerically ordinary space may be insufficient.

Capture a baseline before `suggest_spacing`. Inspect each proposed delta and its target separation; apply only through `apply_spacing_proposal` against the unchanged base revision. Font Maker cannot render an unapplied proposal: compare its compiled result after application, or test alternatives on a disposable project. Use `set_glyph_metrics` for deliberate departures from the heuristic. Reopen conflicts; never replay stale changes blindly.

## Build coverage from this font

Do not use a fixed list of familiar kerning pairs as the review boundary. List the font's potentially troublesome glyphs and the **side and contour feature** that creates each risk: diagonals, overhangs, open cavities, serifs, tails, dots, accents, or unusual widths. Read the [pair inventory guide](references/pair-inventory.md) when planning a spacing pass. Its common Latin examples are starting points; inspect the actual SVGs and compiled forms to discover additional candidates particular to this design.

For a full kerning pass, expand that inventory into **all ordered combinations with the supported, in-scope neighboring characters**, including uppercase, lowercase, mixed case, figures, punctuation, and symbols. Test both directions and self-pairs; `We`, `eW`, `WE`, and `we` are distinct. Deduplicate exact case-sensitive sequences, not visual resemblance. Include controls outside the risk inventory, so checking only risky glyphs against each other cannot hide gaps such as a diagonal capital beside a round lowercase letter. Pair generation is coverage planning, not a reason to assign nonzero kerning.

A targeted correction may review the reported pair, its shape-related neighbors, and affected regressions without launching a whole-font audit. State that boundary and retain uncovered combinations as unreviewed; do not call a targeted pass comprehensive. Expand the inventory when word proofs reveal a new pattern.

## Test exceptions skeptically

Treat every tested pair as unproven until visually inspected in isolation and context. Start assuming issues remain, but do not invent defects to satisfy that assumption. Before clearing a pair, explain its white-space shape and apparent area, closest outline approach, and relationship to neighboring gaps. “No collision,” “equal bearings,” and “looks fine” are insufficient by themselves. Uncertain cases stay unresolved.

Verify that the specimen contains the **exact case-sensitive sequence**: `Typography` contains `Ty`; `rare` contains `ra`; `more` does not contain `ro`. Pair coverage and actual substitution must be checked, not inferred from a plausible word.

Use groups only for genuinely equivalent relevant sides. Inspect each member's geometry and exceptions; a common character category or similar name does not establish class equivalence. Check accented and punctuation members before accepting a class value. Compare kerning off/on while holding other features fixed, at reading and display sizes and inside words. Numeric advance changes reproduce the result but do not decide which looks better.

## Re-space ligature replacements

A replacement is a new drawing. Its left edge, right edge, and advance are new shapes, not the first and last components' shapes, so it inherits neither their sidebearings nor their kerning automatically. Treat every replacement as unspaced until proven, and treat any redraw or advance change as reopening that proof.

For each replacement, compare its left and right white space and edge contour against the first component's left side and the last component's right side, in isolation and in context (`a…b`, inside brackets, inside real words) with the replacement enabled and kerning off/on. Uneven space inside the replacement's own box—a chevron floating a cell further from its neighbor than the bars do—belongs to its drawing or advance, not to pair kerning.

Copy a component's kerning pairs onto a replacement only where that boundary's contour is actually unchanged. A baseline ellipsis can keep the tuck-under values that `T.`, `F.`, and `r.` earned; a range operator whose dots were lifted to mid-height cannot, because nothing tucks under anymore. When replacement edges move, remove stale copied pairs rather than layering new ones on top.

Symbol-like replacements—arrows, equality and comparison operators, hearts, faces—usually deserve more room than letters: an extra unit of white space on each side keeps the symbol visible against surrounding text instead of reading as a letter cluster. Punctuation-like replacements such as `..`, `::`, and `||` keep ordinary letter spacing. Decide this from context proofs, not from equal numbers.

## Separate spacing, visual weight, and drawing

Open forms such as `r` can leave a large lower cavity while their shoulders are already close. Compare `rare rara parallel` and contexts containing `re ro ar`. Tightening further may pinch the shoulder before balancing the cavity; consider outline refinement or a coordinated replacement instead.

Review punctuation attachment **and weight**. Compare colon/semicolon dots with period, comma, and the `i` dot in real text. Oversized marks or off-center forms cannot be repaired merely by squeezing bearings. Explain their apparent weight, placement, and white space relative to the line; route construction issues to [outline QA](../font-outline-qa/SKILL.md) and [specimen review](../font-specimen-review/SKILL.md).

Creative joins may be worth exploring even when spacing is acceptable; record opportunities separately from defects. Use [ligature design](../font-ligature-design/SKILL.md) for original shared drawings. Never derive repairs from existing fonts. AI concepts can suggest rhythm but cannot supply reliable numeric kerning or unchanged control shapes.

Extreme kerning that changes perceived identity—for example `nn` reading as `m`—requires a concrete comparison and approval unless full creative freedom was explicitly granted. Keep unapproved fusions out of the active font. Routine recognizable corrections need no extra consultation.

## Generate and inspect repeatable proofs

Use the bundled [proof script](scripts/render_kerning_proofs.py) following its [usage and feature contract](references/proof-script.md). It produces labeled OFF/ON sheets, a compiled-font snapshot, hashes, shaping traces, and **pending** review entries. Generate the planned ordered pair matrix with explicit left/right character sets and both directions, then add context words containing those exact sequences. Default samples are smoke checks, not the inventory. Missing-glyph skips are incomplete coverage, not passes.

Keep SVGs and use PNG `pixel_scale=3` for spacing diagnosis, `4` for join detail, plus separate `1` previews at actual small reading size. Record `font_size` and scale. Split large sheets; upscaling a low-resolution bitmap adds no evidence. Open the actual images before making judgments.

The script fixes `dlig` off and `rlig` on; it does not certify discretionary ligatures. Use `preview_font` and `shape_text` with explicit features to check replacement boundaries, holding the replacement enabled while toggling kerning. Internal ligature spacing belongs to its drawing/advance, not boundary kerning.

Record image, project revision, font-byte hash, exact pair/text, feature map, sizes, observation, reason for acceptance, and unresolved action. Keep a case-sensitive coverage ledger that distinguishes planned, generated, inspected, accepted, and unresolved evidence; report counts and exclusions without clearing untested combinations. A contact sheet or shaping trace alone does not establish inspection. Recheck affected entries after outline, metric, or kerning changes.
