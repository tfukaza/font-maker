---
name: font-production-workflow
description: Run an original Font Maker project from scope and provenance through aligned SVG production, coverage gates, revision-safe layout, export, and interactive specimen handoff. Use for creating or extending a font; route isolated drawing, spacing, or acceptance to the focused skills.
---

# Font Production Workflow

Treat `font.yaml` and canonical SVGs as authoritative; fonts, proposals, previews, and HTML specimens are derived. Compile early and inspect rendered images at each gate. Validation proves technical properties, not visual quality.

## Choose the current phase

- Drawing: choose the relevant style guidance below, then use [design metrics](../font-design-metrics/SKILL.md) and [SVG production](references/svg-glyph-production.md).
- Import and contour repair: [outline QA](../font-outline-qa/SKILL.md).
- Stable shapes ready for layout: [spacing and kerning](../font-spacing-kerning/SKILL.md).
- Coordinated replacement drawings: [ligature design](../font-ligature-design/SKILL.md).
- Acceptance and regression: [specimen review](../font-specimen-review/SKILL.md).

Load only references needed for the current phase. Focused skills remain usable on their own.

Before drawing or refining shapes, load the applicable style skill:

- [Pixel and modular fonts](../font-pixel-design/SKILL.md): module grids, step rhythm, and crisp or deliberately softened construction.
- [Serif fonts](../font-serif-design/SKILL.md): contrast, stress, serif attachments, bowls, and terminal families.
- [Sans-serif fonts](../font-sans-design/SKILL.md): proportions, apertures, joins, stroke balance, and differentiation.

Use only the styles relevant to the brief; a hybrid may need selected guidance from more than one. These skills supplement the shared pipeline rather than replace it. Do not force an unrelated style into one of these categories or load drawing guidance for an export-only task.

## 1. Agree on scope and original provenance

Record intended use, direction, family/style, formats, character profile, language claims, and optional feature ambitions. If direction is unresolved, compare concepts with identical text and presentation before expanding the set.

Keep the original concept and approved changes available to reviewers. Record its defining proportions, curvature, terminals, weight, and joins; compare compiled proofs against that source, not only the last iteration. A readable but stylistically drifting glyph remains unresolved until corrected or the changed direction is approved.

Draw every typeface from scratch. Never import, trace, transform, interpolate, or derive outlines from existing fonts, including installed or dependency-bundled fonts. A concept image may guide visual qualities; it is not permission to copy an existing typeface. Reuse this project's own original base, accent, and component constructions where appropriate. Record original hand drawing, project-specific procedural geometry, or user-supplied original artwork as provenance.

Choose coverage using the versioned [Unicode inventory](references/latin-coverage.json) and [coverage audit](references/latin-coverage.md):

- **Focused study:** the user-specified subset, explicitly labeled incomplete.
- **Prototype:** 103 encoded characters—printable ASCII U+0020–U+007E plus U+2013, U+2014, U+2018, U+2019, U+201C, U+201D, U+2022, and U+2026.
- **Latin display release:** the union of that prototype and Monotype's downloadable recommendation, currently **191 unique codepoints**. Preserve existing symbols even when the external list omits them.

Monotype describes its 186-glyph recommendation as a minimum for Latin display fonts serving some major Western languages, not every Latin-script language. The JSON records source, retrieval date, exact spreadsheet inventory, and discrepancies; do not silently repair it from memory. Add language-brief requirements separately. Never claim broader support without language-specific coverage, shaping, and visual checks. Match coverage across styles in a family.

A default space, `.notdef`, unmapped ligatures, fallback rendering, or unrelated drawings mapped onto missing letters do not fulfill the design brief. Design distinct uppercase/lowercase forms and figures unless the brief explicitly requests otherwise. Use an explicit space when its width is a design decision.

## 2. Establish construction before mass drawing

Create or open the project and inspect its revision. Use the generated template: shared viewBox, one baseline, UPM, ascender, cap height, x-height, descender, and canonical transform. Changing metrics regenerates guides without rescaling existing artwork.

Approve a small original control set first: `H O n o`, diagonals, ascenders, descenders, and punctuation. Record stroke families, overshoot zones, terminals, joins, counters, and tolerances. Metrics make construction repeatable; retain optical corrections supported by rendered comparisons.

Produce closed filled SVG outlines inside `#glyph`, never cropped artboards. Set stable names, explicit encoded mappings, and deliberate advances. Import coherent batches with `upsert_glyphs`; a rejection means no glyph in that batch was accepted. Validate and inspect imported font-space bounds after each batch.

Treat scripted or procedural construction as an initial sketch, not finished type design. Before accepting the set, inspect **every glyph individually**, both as a rendered outline beside the original concept and by reading its SVG path geometry. Refine stroke widths, curvature, tangents, counters, aligned edges/vertices, terminal angles, and joins deliberately; a shared helper or a clean validation report does not establish that its output is well drawn. See the [per-glyph refinement gate](../font-outline-qa/SKILL.md#per-glyph-refinement-gate). Preserve hand-refined source paths when rerunning generators. Do not package a generated alphabet as visually finished while this pass is incomplete.

For accents, reuse only original project components as flattened outlines. Review placement, dots, and clearance through the metrics skill. This workflow does not require mark anchors or complex positioning.

## 3. Establish spacing and intentional features

Set sidebearings with kerning disabled before pair exceptions. A gap following a glyph across neighbors usually calls for metrics or outline refinement. Inspect proposals from `suggest_spacing` before applying; heuristic regularity is not optical rhythm. Word spaces must read distinctly from internal gaps.

Use the spacing skill's [glyph risk inventory and ordered-pair coverage](../font-spacing-kerning/references/pair-inventory.md) to discover issues from the actual contours and test all in-scope neighbor combinations; a fixed sample-pair list is not a full kerning review.

Use `set_kerning` for justified groups and exceptions. Explore ligatures from the design's gestures, not a compulsory `fi/fl` inventory. Import original replacements before `set_ligatures`; optional expressive combinations normally belong in `dlig`.

Inspect ordinary, kerning-only, and substituted words using explicit feature maps and actual shaping traces. Unconventional joins or extreme kerning that change perceived letter identity require a concrete comparison and approval before promotion unless full creative freedom was explicitly granted. Keep unapproved studies isolated; optional features do not waive this boundary.

## 4. Review, export, and hand off

Retain SVG proofs; use PNG `pixel_scale=3` for reading/spacing diagnosis and `4` for joins, plus separate `pixel_scale=1` at the actual small reading size. Record `font_size` and scale; split oversized sheets instead of upscaling low-resolution images.

Use specimen review to inspect weight, word boundaries, differentiation, punctuation, accents, and active substitutions. Test words must actually contain each target sequence. Distinguish generated, inspected, accepted, and unresolved evidence. If image inspection is unavailable, visual acceptance remains pending.

Run `validate_font_project` with a temporary build and export the reviewed revision. Compare **each exported font's Unicode cmap** with the selected inventory; report exact missing codepoints, not just a count. Shape and visually inspect required characters and replacements. Record paths, SHA-256, revision, formats, backend versions, active features, and remaining diagnostics.

Include local `specimen.html` for deliverable prototypes and releases, reusing an existing page when available. Follow the [interactive specimen checklist](references/interactive-specimen.md): current font bytes, editable text, size/features, accurate loading/coverage warnings, downloads, and browser verification. The page complements static proofs. Report browser checks as pending when unavailable.

Keep generated-font licensing metadata and the user's licensing decision separate from Font Maker's GPL license; do not automatically assign GPL to the font.

## Revision safety

Read the current revision before a durable mutation and carry forward its returned revision. On `REVISION_CONFLICT`, reopen and inspect changes; never replay blindly. Regenerate proposals after intervening source changes. Fix source files, never exported binaries. Hand off accepted scope and unresolved work rather than calling an incomplete study a full release.
