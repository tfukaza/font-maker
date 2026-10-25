---
name: font-design-metrics
description: Establish a font's shared SVG coordinate contract, vertical metrics, stroke families, optical compensation, and accent placement. Use when drawing original glyphs or diagnosing scale and alignment drift; not for OpenType authoring or spacing-only review.
---

# Font Design Metrics

Draw original glyphs within one measurable system. Never borrow, trace, or transform existing font outlines. Reuse this project's own original bases and accents when genuinely shared; preserve provenance and deliver flattened outlines.

Measurements expose drift and repeat successful decisions. Actual compiled images establish apparent alignment, balance, counters, weight, and personality. Preserve deliberate asymmetry or compensation when equal geometry looks unequal; nominal metrics alone never establish acceptance.

## Establish the coordinate contract

Read the manifest and generated template before drawing. Its UPM, transform, viewBox, guides, and advance-width source are authoritative. A typical Latin display starting point at 1000 UPM is:

| Metric | Font-space value |
| --- | ---: |
| Ascender | 800 |
| Cap height | 700 |
| x-height | 500 |
| Baseline | 0 |
| Descender | -200 |

These are starting ratios, not universal requirements. Choose UPM once; do not scale individual glyphs to fill their canvas. Font y increases upward; SVG y normally increases downward. The canonical transform is:

```text
font_x = (svg_x + translate_x) × scale
font_y = (baseline_y - svg_y + translate_y) × scale
```

At scale 1, translation 0, and SVG baseline 800, SVG y=100 maps to cap height 700; y=300 to x-height 500; y=800 to baseline 0. The importer flips y **once**. Never pre-flip artwork.

Preserve the shared viewBox, origin, units, and single baseline. Draw in `#glyph`; keep secondary guides in the ignored group. Do not crop each SVG to its outline. Font Maker stores advance independently of canvas width. Changing metrics changes guides, not existing glyph scale: recheck affected glyphs deliberately.

Keep glyph names case-sensitive but make authored filenames collision-safe, for example `glyph-U004F.svg` and `glyph-U006F.svg`, not `O.svg` and `o.svg` on a case-insensitive filesystem. Confirm each imported outline belongs to the intended glyph.

## Establish measurable families

Begin with `H O n o`, then an ascender, descender, diagonal, narrow glyph, and dot. Record uppercase and lowercase vertical stem widths separately; in contrast designs also record thick/thin families. Include horizontals, round sides, diagonals, terminals/corners, crossbars, dots, and overshoot zones as relevant.

Measure like with like away from joins, tapers, and extrema. A horizontal may need to be thinner than a vertical to look equally heavy. Rounds and diagonals may need their own compensation; do not force everything into one width.

Measure diagonal strokes **perpendicular to their edges**, not by their horizontal or vertical span. Equal coordinate spans can leave a diagonal physically thinner than an upright; even equal perpendicular thickness can look unequal in context. Compare diagonal letters, figures, and symbols with their own upright and round controls at display and intended reading sizes. Add or remove thickness only where the compiled proof supports it: long uninterrupted diagonals and crowded joins can already look too heavy. Preserve the design's thick/thin contrast, counter space, and intended parallel edges. Record the before/after measurements and visual reason; do not apply a universal thickening percentage or assume that every diagonal needs the same correction.

Set reference values, expected members, and useful tolerances. Without a project-specific range, a deviation of more than a few percent among supposedly equivalent straight stems is an inspection flag, not an automatic failure. Compare outliers beside controls, correct drift, and document visually justified exceptions. When the family reference changes, recheck every affected member.

### Audit perceived stroke weight

When reviewing weight, inventory every delivered glyph by construction family, including figures and punctuation. Review each glyph in clean compiled proofs, repeated sequences, and words or numeric contexts at display and native small sizes. For each family, compare apparent darkness with approved controls and inspect the source geometry: straight sections, curved thick/thin transitions, diagonals, crossbars, terminals, dots, and accumulated mass at joins. A parallel outline can still be optically too heavy; equal maximum widths can hide different distributions of black and counter space.

Use measured slices to diagnose a visible imbalance, not as an automatic acceptance score. Separate intended high contrast from inconsistent weight, and do not normalize unlike strokes or resize a whole glyph to repair a local issue. Test restrained alternatives for outliers, then record the chosen correction or reason to retain each glyph, the inspected proof sizes, and the compiled font revision. Recheck affected spacing and related components after changes. Earlier geometry acceptance does not clear a newly reported optical imbalance.

### Design the distribution of weight

If uniform thickening or thinning leaves a glyph unbalanced, reconsider where its weight belongs. Explore deliberate width profiles: a light entry that grows toward a grounded terminal, a tapered diagonal, a relieved join, a stronger foot, or a thinner crossbar paired with a fuller main stroke. Related glyphs can suggest useful contrast relationships without donating their exact outline. A glyph can need both lighter and heavier regions at once.

Compare a small set of structurally different candidates in compiled text; do not just repeat smaller versions of the same unsuccessful construction. Judge the silhouette, direction, counter space, and apparent mass beside neighboring forms and the reference. For variable-width strokes, measure several sections along the stroke and inspect their transition through SVG endpoints and handles. Avoid unintended bulges, abrupt weight steps, or weak joins. Preserve deliberate contrast rather than treating constant thickness as a quality requirement.

Parallelism and shared angles establish a design system, but intentional taper can be the better optical solution when the brief permits it. Keep unaffected alignments coherent and document which edges diverge, the visual reason, and the before/after evidence. A user's request for a taper or other weight modulation takes precedence over an earlier general preference for parallel edges.

## Align flat and optical extrema

### Audit the whole metrics system

Run this consistency pass on the first control set, every expanded or revised glyph family, and the final compiled exports. Record each applicable target or range, participating glyphs, actual measurements, and justified exceptions. Recheck related glyphs when a reference value changes; a manifest edit alone does not repair geometry.

| Metric family | Required consistency check |
| --- | --- |
| Coordinate scale and origin | Shared UPM, transform, baseline, and source canvas; no per-glyph scaling or accidental translation. |
| Baseline and lowercase body | Flat bottoms and body tops follow their intended baseline/x-height zones; separate dots and accents from the body. |
| Capitals and ascenders | Check flat cap tops together, and ascenders such as `h b d k l` against their declared family. Capitals and ascenders may have different intended heights; do not conflate them. |
| Descenders | Check `p q g j y` against their intended depth and terminal families. Different constructions can have deliberate depths, but each exception needs a reason rather than unexplained drift. |
| Overshoot and curved extrema | Comparable rounds and pointed forms follow documented optical zones at baseline, top, or descender; inspect perceived alignment as well as bounds. |
| Stroke and repeated-component dimensions | Compare equivalent stems, horizontals, thick/thin strokes, bowls, crossbars, terminals, corners, and joins within their named families and tolerances. |
| Dots, accents, and punctuation | Check related mark dimensions, position, and clearance from the body and neighbors. Review punctuation's intended alignment zones and apparent weight; not every dot-like mark needs identical geometry. |
| Advances and sidebearings | Check deliberate width classes, spacing groups, and advance/bounds/bearing relationships. Tabular figures share advances only when intended; proportional letters and figures must not be forced to equal widths. |
| Figure alignment | Check the declared numeral style: lining figures share their intended top/bottom zones; oldstyle figures may deliberately ascend or descend. |
| Line and clipping metrics | Compare the tallest accents, deepest descenders, and approved flourishes with exported ascent/descent and line-gap settings. Inspect stacked lines and target-renderer clipping; line metrics need not equal any one glyph's bounds. |

Verify values in both the imported outlines and actual compiled output where applicable; conversion, rounding, or stale exports can invalidate source-only evidence. Use guides to locate discrepancies and clean specimens to judge their visual consequence. Unexplained deviations remain unresolved even if all contours validate. Do not retroactively label an accident an optical correction: support exceptions with a measured comparison and the approved design intent.

### Check vertical construction in context

Flat bottoms meet baseline; flat capitals meet cap height; flat lowercase tops meet x-height. Ascender and descender endpoints follow their guides. Curved or pointed terminals may use shared optical zones beyond them.

Treat these as explicit construction checks, not merely manifest values. For each related glyph family, record the relevant body baseline/top, cap or ascender top, descender bottom, and any optical exception; compare the **compiled outline** with those targets. A correct declared x-height or `OS/2.sxHeight` does not prove the actual drawings follow it. Do not lower the shared metric to accommodate one accidentally short glyph or rescale the whole glyph to hide a local problem.

For Latin dotted letters, measure the lowercase **body separately from the dot**. Compare the stem tops of `i` and `j` with `n` and `x` where their construction calls for the same x-height; whole-glyph bounds include the dot and can conceal a short body. Record dot bounds, body-to-dot clearance, apparent dot weight, and alignment independently. Check accented `i` and dotless `ı` against the same original body when present. If extending a body to the target closes its dot gap, reconsider dot placement too rather than welding the parts together; preserve the intended baseline and descender.

Use `nxin nixn minimum` for body-height comparisons and `njn ijij` for dotted/descending forms, with ligatures disabled so the base glyphs are actually inspected. Compare guide-overlaid and clean compiled proofs at reading and native small sizes. Keep unexplained discrepancies unresolved; an intentional stylistic exception needs measured values, a visual reason, and evidence that it fits the approved concept, not a blanket appeal to optical judgment.

Cap height, x-height, and these control letters describe Latin construction. Do not force Japanese kana or kanji onto Latin lowercase/capital zones; use script-specific body and alignment conventions while preserving the shared import coordinate transform.

At 1000 UPM, **10–20 units equals 1–2% of the em**, not 1–2% of cap height or x-height. This is only an initial overshoot experiment: judge `O` against `H` and `o` against `n` in rendered text, then record chosen zones. Ensure the source canvas and exported line metrics do not clip overshoots.

Infer reference-image alignments from repeated stable forms, not one raster bounding box. Antialiasing, perspective, and cropping can distort measurements. Reuse construction logic rather than independently stretching completed letters onto guides.

## Place accents as part of the design

Use the [coverage profile](../font-production-workflow/references/latin-coverage.md) to identify required precomposed glyphs. Draw original accent families with coherent weight, angle, curvature, and separation. Reuse project bases and marks as **flattened outlines**; neither mark anchors nor complex-positioning support is implied.

Review each mark over narrow/wide capitals and lowercase—for example `Í/Ó` and `í/ó`—and over rounds, diagonals, and flat tops. Optical placement follows apparent center and slant, not just bounding-box midpoint. Uppercase marks may need different height or proportions while remaining related.

Handle dots deliberately: precomposed accented `i` normally replaces its ordinary dot with the accent; do not stack both accidentally or lose a language-required distinction. Keep dotless `ı` distinct. Check cedillas and other below-base forms against descenders and baseline rhythm.

Verify clearance above capitals and below baseline, stacked lines, canvas bounds, and actual exported clipping. Do not squeeze accents against a cap merely to fit an old guide. Test accented bearings and kerning-group membership; the base's spacing does not prove accent clearance. Broader language claims require explicit checks, including required sequences outside precomposed coverage.

## Prepare and inspect the batch

Use closed filled outlines, real counter contours, economical curves, and flattened transforms. SVG paths can contain **lines, quadratic and cubic Béziers, and arcs**; they are not exclusively cubic. The importer normalizes supported geometry; TrueType compilation may introduce cubic-to-quadratic conversion. Inspect that output. Use [SVG production](../font-production-workflow/references/svg-glyph-production.md) and [outline QA](../font-outline-qa/SKILL.md) for detailed import rules.

Record bounds and an intentional advance:

```text
LSB = xMin - originX
RSB = advanceWidth - xMax
```

Do not mathematically center every glyph. Establish control rhythm with kerning off; route repeated spacing problems to [spacing and kerning](../font-spacing-kerning/SKILL.md), not ad hoc scaling.

Import with the latest revision, validate each batch, and compare imported extrema with recorded zones. Reopen on conflict. Report technical findings with measured invariants and visual findings with visible effects.

Keep SVG proofs and PNGs at `pixel_scale=3` for alignment/spacing and `4` for outlines. Also render `pixel_scale=1` at actual small text size. Record size and scale, split long lines, and inspect clean images without guides. Include accents, punctuation, repeated forms, mixed case, and words, not just alphabet rows. If images cannot be inspected, mark aesthetic acceptance pending.
