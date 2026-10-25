---
name: font-specimen-review
description: Review compiled font evidence for concept fidelity, visual balance, spacing, differentiation, coverage, and regressions across sizes and features. Use for independent visual acceptance and release checks; not for judging uncompiled SVG artwork alone.
---

# Font Specimen Review

Review the compiled font at one identified revision. Record exact text, feature settings, size, pixel scale, font-byte hash, and artifact paths. Validation is not an aesthetic score: open actual PNGs or rendered SVGs with image-understanding capabilities. If image inspection is unavailable, visual acceptance is pending.

For a newly generated or substantially redrawn set, require the [per-glyph visual and SVG refinement pass](../font-outline-qa/SKILL.md#per-glyph-refinement-gate) before visual acceptance. Alphabet sheets and scripted metric audits complement that pass; they do not substitute for it. Keep user-rejected glyphs unresolved until their drawings have been corrected and rechecked against the original concept.

## Check concept fidelity explicitly

Keep the **original concept art and/or approved design direction** beside the compiled specimen. Do not compare only with the previous generated iteration; a sequence of individually plausible edits can drift far from the brief.

Record the defining traits before judging: silhouette, proportions, stroke modulation, terminals, curvature, counters, joins, and overall mood. Compare shared reference letters and matched words at comparable apparent size. For new characters absent from the reference, explain how their construction extends those traits.

Look specifically for drift such as soft swollen terminals becoming pointed hooks, fluid bowls becoming tense wedges, or square modules becoming round bubbles. Do not impose “everything rounded” if the reference includes deliberate sharp details: judge their location, frequency, and role. Separate unavoidable optical correction from a changed visual language. Identify the glyph, visible departure, reference evidence, and proposed action.

A readable, well-kerned glyph can still fail style fidelity. Treat unapproved material drift as unresolved; show a comparison and obtain direction before adopting it as the new style. Record approved departures explicitly. Give independent reviewers the original reference as well as the current proof.

## Review optical balance and technical consistency

First judge clean text: apparent ink density, alignment, weight, counter space, visual center, word silhouettes, rhythm, differentiation, and personality. Then use guides, bounds, traces, and measurements to explain findings. Keep intentionally compensated geometry when it works visually.

Compare equivalent straight stems and recurring components against named families and tolerances. Unexplained variation is a defect to investigate, but verticals, horizontals, rounds, and diagonals need not share one literal width.

Explicitly audit script-appropriate height and alignment families against the compiled drawings, not only declared metrics: baseline, Latin x-height and cap height, ascender/descender zones, and documented overshoot. For Latin `i`/`j`, inspect body tops separately from dots beside `n`/`x`; a high dot can conceal a low stem in whole-glyph bounds. Compare guide-overlaid and clean views, record actual versus target values, and leave unexplained drift unresolved. Use the [metrics checks](../font-design-metrics/SKILL.md); do not impose Latin height categories on Japanese glyphs.

Require the complete applicable metrics audit—not just x-height—before acceptance: cap and ascender families, descender depths, stroke/component dimensions, mark clearances, numeral style and width classes, advances/bearings, and exported line/clipping metrics. Record pass, justified exception, unresolved, or not applicable for each family with evidence. Review after control-set approval, batch expansion, and related metric changes; do not postpone consistency checks until the final specimen. Different families may have different targets, but unexplained variation within a family is not cleared by a visually pleasing sample word.

Scrutinize punctuation alongside related marks and in context: period, colon, semicolon, comma, and `i` dot; `12:30`, `a;b.`, quotes, and monetary figures. Adequate clearances do not excuse oversized dots or an off-center tail. Explain apparent prominence, placement, white space, and fit with neighboring text. “Consistent metrics” and “no collision” are not enough. Apply the same scrutiny to letters and numerals.

## Build coverage-driven proofs

Use the [targeted corpus](references/test-corpus.md) as a starting sample, not an exhaustive checklist. Include controls, word spaces, diagonals, open forms, mixed case, repeated letters, figures, symbols, differentiation, and every actual feature-triggering sequence.

Verify exact case-sensitive target occurrences before rendering: plausible words may not contain the pair being claimed. Check shaping reaches the intended replacement. Compare ordinary, kerning-only, and ligature versions; isolate one feature at a time with explicit maps. Preserve glyph names/clusters in kern-only comparisons; confirm only intended substitutions and coherent clusters in ligature comparisons. Exercise competing sequences and replacement boundaries, not just internal joins.

Audit the [selected coverage inventory](../font-production-workflow/references/latin-coverage.md) against every exported Unicode cmap: focused study, 103-character prototype, or 191-character Latin display release baseline. Report exact missing codepoints. Unmapped replacements, fallback, and `.notdef` do not count. A prototype does not become a release merely because its alphabet looks finished.

Review accents over narrow/wide caps and lowercase: mark-family consistency, optical placement, dot handling, vertical clearance, stacked lines, clipping, and spacing. Precomposed coverage is not proof of combining-mark positioning or every Latin language. Require language-specific tests before broader claims and matching coverage across family styles.

## Require inspection-resolution evidence

Keep SVG companions. Use `preview_font` PNG `pixel_scale=3` for reading and spacing diagnosis and `4` for large outlines/joins. At `font_size=96` and cap height 700/1000 em, 3× provides roughly 202 cap-height pixels; actual metrics affect this. Record size and scale, not merely “high resolution.”

Make separate `pixel_scale=1` proofs at actual small reading sizes to judge raster behavior. Split long sheets so viewers do not shrink everything; preserve target sequences and context when splitting. A low-resolution or enlarged bitmap leaves close inspection incomplete. Use overlays for diagnosis but always review a clean counterpart.

## Independent review and evidence states

For substantial revisions, use independent subagents when available. Divide failure modes—base spacing/word boundaries; risky pairs; differentiation/small-size reading; figures/punctuation/accents; outlines/concept fidelity. Give raw proofs, original references, exact settings, and focused strings, not another reviewer's conclusions. One integrator reconciles findings, renders contested cases, and owns mutations. Review is not a vote.

Assume issues remain and require concrete evidence before clearing each case, without inventing defects. For spacing, explain white-space shape, closest approach, and surrounding rhythm; for style, compare specific reference traits; for balance, explain prominence and placement. Record:

- **Generated:** artifact exists, not yet viewed.
- **Inspected:** image was viewed and an observation recorded.
- **Accepted:** explicit visual reasons and required technical checks support clearance.
- **Unresolved:** ambiguous evidence, missing coverage, unapproved drift, or a known defect remains.

The [kerning proof script](../font-spacing-kerning/references/proof-script.md) starts cases pending; generation never clears them. State reviewed scope and leave untested combinations unclaimed.

For regression fixes, regenerate the same words/settings from the new revision and verify font-byte hashes. Route systemic height or weight findings to metrics/outlines, repeated spacing to bearings, and neighbor-specific gaps to kerning. Do not approve because one number improved.

A deliverable also needs a local interactive specimen checked using the [handoff checklist](../font-production-workflow/references/interactive-specimen.md). Verify actual loaded bytes, coverage warnings, controls, and downloads; browser failure means that check is pending. Interactive tests complement, not replace, high-resolution proofs.
