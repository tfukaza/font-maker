# SVG glyph production

Read this when constructing or revising SVGs. The project's template and manifest override examples. Draw from scratch, never from existing font outlines; reuse only this project's original constructions with recorded provenance.

## One coordinate contract

A typical 1000 UPM project uses:

```text
viewBox: 0 0 1000 1000
SVG baseline: y = 800
font_x = (svg_x + translate_x) × scale
font_y = (baseline_y - svg_y + translate_y) × scale
```

With default scale/translation, SVG y=100 maps to font cap height 700; y=300 to x-height 500; y=800 to baseline 0; y=1000 to descender -200. The importer performs the y inversion once. Do not pre-flip or crop individual artboards. Outline bounds, sidebearings, advance, and canvas width are distinct.

Use [design metrics](../../font-design-metrics/SKILL.md) for stroke families, overshoot, tolerances, and accent placement. Infer a concept's skeleton, modulation, terminals, counters, joins, and width classes, then approve original controls before mass drawing. Never trace antialiased edges point by point or stretch finished glyphs onto guides.

## Import-safe structure

Draw inside `#glyph`. Keep guides in `#fontmaker-guides` with `data-fontmaker-ignore="true"`; normalization removes them.

Deliver supported closed filled geometry. Font Maker normalizes supported primitives and affine transforms, but clean sources avoid unnecessary transforms. It rejects:

- strokes and open contours;
- SVG text and embedded rasters;
- scripts, external links, stylesheets, and `<use>`;
- masks, filters, clipping, and ambiguous hidden artwork;
- excessive file size or point complexity;
- fill behavior whose counters cannot be interpreted safely.

Expand strokes before import. Flatten transforms, remove construction objects, delete duplicate/stray points, and close contours. Use real counter contours with compatible winding, not white painted shapes. Precomposed accents may reuse original project bases and marks as flattened paths, without adding mark anchors.

## Curves and contacts

SVG paths support lines, quadratic and cubic Béziers, and arcs; supported geometry is normalized by the importer. Place economical segments at meaningful extrema and transitions. Align tangent handles at smooth joins unless the reference calls for a corner.

Inspect kinks, flat extrema, microscopic segments, self-intersections, retraced edges, near-coincident contours, and counters that close at small size. For liquid modular designs, follow [outline QA](../../font-outline-qa/SKILL.md): square terminals, tangent concave fillets, restrained diagonal necks, no circular-overlay knots.

Compilation may remove overlaps, correct direction, add extrema, and round coordinates. These operations cannot supply design judgment. Inspect compiled TTF as well as normalized SVG for cubic-to-quadratic distortion and changed counter geometry.

## Names, mapping, and metrics

Use stable glyph names such as `A`, `adieresis`, `uni20AC`, or `f_i`, preserving case. For authored source filenames, use codepoint or collision-safe identifiers such as `glyph-U004F.svg` and `glyph-U006F.svg`: `O.svg` and `o.svg` can overwrite one another on case-insensitive filesystems even though the glyph names are distinct. Check source paths are unique under case folding, including unmapped replacement filenames.

Assign explicit Unicode only to encoded characters. Replacement glyphs normally remain unmapped; check exported cmap too rather than trusting names or source declarations.

```text
LSB = xMin - originX
RSB = advanceWidth - xMax
```

Set deliberate advances and optical bearings, not automatic mathematical centering. Negative bearings may be intentional on diagonals or overhangs.

## Productive batch order

Start with `H O n o`; add `A V I l i`, an ascender and descender, then related alphabet families, figures, space, punctuation, accents, and symbols from the selected coverage profile. Draw ligature components before replacements; `fi/fl` are examples, not compulsory inventory.

For each coherent batch:

1. Check shared canvas/baseline, ignored guides, and glyph content.
2. Confirm names, mappings, advances, and intended bearings.
3. Import using `upsert_glyphs` with the current revision; any error rejects the whole batch.
4. Validate and inspect normalized font-space bounds.
5. Shape and preview controls and words with explicit features, initially kerning and ligatures disabled.
6. View the actual images beside the original direction, repair source SVG/metrics, and repeat.

Compile early: origin, winding, mapping, and advance mistakes are cheaper to catch in a small control batch. Follow the calling skill's high-resolution and native-size proof requirements; an unviewed generated sheet is not visual acceptance.
