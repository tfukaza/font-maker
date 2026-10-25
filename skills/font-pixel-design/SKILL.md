---
name: font-pixel-design
description: Draw or refine original pixel and modular-grid glyphs with coherent cell geometry, step rhythm, counters, and intentional contact treatment. Use for pixel-specific construction and optical decisions; not for export-only or spacing-only work.
---

# Pixel Font Design

Use this skill for the drawing decisions particular to pixel and modular fonts. Keep provenance, coordinates, coverage, and delivery in the [production workflow](../font-production-workflow/SKILL.md); use [design metrics](../font-design-metrics/SKILL.md) for shared measurements and [outline QA](../font-outline-qa/SKILL.md) for every glyph's visual and SVG review.

## Establish the grid and rendering intent

Record module size, grid origin, nominal stem widths in cells, body-height rows, and target rendering sizes. Decide whether advances are monospaced or proportional; a grid does not imply a monospaced font. Preserve the shared font coordinates rather than giving each glyph its own independently fitted grid.

Choose the treatment from the brief or approved controls:

- **Crisp grid:** contours follow the intended cell lattice and exposed corners stay square. Do not introduce curves, rounded terminals, or half-cell adjustments merely to imitate a conventional outline font.
- **Deliberately softened modular:** retain recognizable modules and straight runs while specifying which contacts, internal corners, or exposed corners may change. Use the outline QA guidance on surface-tension connections only when that treatment matches the design. Do not smooth every corner or apply circles globally to connect modules.

A rounded pixel brief can authorize rounded exposed corners; record that as its own treatment rather than assuming all modular fonts need it. Keep deviations local and reproducible.

## Draw with intentional step rhythm

Use a small control set that exercises straight stems, stepped rounds, diagonals, narrow forms, and junctions, such as `H O n o A V W i`. Derive related forms from the same cell logic while preserving their distinct construction.

Design diagonal and curved staircases as visible run sequences. Compare changes in run length, mirrored directions, and the transition into straight stems. A one-cell offset can create an unintended tooth, flat spot, or lopsided bowl; do not trust a smooth mathematical curve rasterized onto the grid to choose those steps well.

Compare the apparent weight of stepped diagonals with upright strokes. Count local cell coverage and inspect negative-space width around joints; indiscriminately adding a full row can make one diagonal much darker. Choose a supported grid resolution or a deliberate sequence of steps when the current lattice cannot express the desired weight. Preserve approved asymmetry where a mirrored cell pattern reads unevenly.

Keep counters and apertures open at the target size. Check narrow interior channels, diagonal-only contacts, stacked junctions, and close terminals for pinholes, accidental bridges, or disconnected fragments. A contact visible at large scale may vanish at native size; intentional separated modules should remain visibly separated.

## Make grid-compatible optical corrections

Judge apparent alignment before borrowing smooth-outline conventions. A full-cell overshoot may be excessive on a coarse grid, while a half-cell overshoot may violate the crisp rendering intent. Use flat or stepped extrema and permitted cell changes first; document finer-grid or off-grid exceptions only when the design and target renderer support them.

Size dots, punctuation, and accents as part of the module vocabulary. One-cell dots are not automatically sufficient: compare their apparent weight, separation, and recognition with the body at the intended size. Preserve distinguishable `i/j/l/1`, `O/0`, and related forms within the available cells.

## Inspect in the intended raster conditions

Pair enlarged cell-level proofs with native-size compiled text. Inspect integer module-to-pixel scales for crisp pixel delivery, and the actual fractional CSS sizes or scaling conditions expected when the font is used as a scalable display face. Antialiasing at one scale must not disguise an accidental cell or broken contact.

Review changed glyphs in words as well as on the grid. Route advances, sidebearings, and pair decisions through [spacing and kerning](../font-spacing-kerning/SKILL.md), retaining any declared grid or monospace constraint. A clean grid is construction evidence, not acceptance of the final silhouette.
