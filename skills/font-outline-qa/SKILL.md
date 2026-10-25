---
name: font-outline-qa
description: Inspect and repair import-safe SVG geometry, contours, tangent joins, surface-tension connections, and compiled outline defects. Use for import failures or shape cleanup; not for spacing-only review.
---

# Font Outline QA

Inspect source SVGs and compiled fonts. Draw repairs from scratch or reuse this project's own original components; never import, trace, or transform existing font outlines. Technical validity is necessary, but visual inspection decides tension, balance, and concept fidelity.

## Import-safe geometry

Keep artwork in the template's single `#glyph` group on its unchanged viewBox and baseline. Deliver closed filled outlines with expanded strokes and flattened transforms. Remove text, rasters, clipping, masks, filters, external resources, hidden construction objects, stray points, zero-length segments, and microscopic contours. Never use white paint to fake counters.

Preserve intentional overlaps in editable originals if useful, then verify build-time cleanup. Counters must survive normalization and direction correction. Prefer economical curves with meaningful extrema and tangent continuity, avoiding point-heavy traces and retraced edges. SVG supports quadratic and cubic curves; inspect TrueType conversion, rounding, and overlap removal for new slivers, spikes, or flat spots.

Compare recurring stems, bowls, terminals, and joins by measurement family, away from tapers and junctions. Investigate unexplained variation without forcing optical corrections or unlike orientations to one width. Use [design metrics](../font-design-metrics/SKILL.md) for that contract.

## Per-glyph refinement gate

Scripts may produce the first sketch and continue to handle construction, compilation, or measurement. They do not replace deliberate glyph-by-glyph refinement. Review every delivered glyph in both forms:

- **Visual:** inspect the glyph on its own at an honest inspection scale, beside the original concept where available, then in words. Compare silhouette, stroke distribution, counter shape, curvature, terminal placement, and related letters. Preserve the reference's distinguishing structures; do not fix a bulge by replacing the bowl with an unrelated generic oval.
- **SVG geometry:** read the actual path commands and inspect endpoints and Bézier handles. Check intended collinearity/parallelism, vertex alignment, stroke thickness through corresponding sections, tangent continuity, extrema, closure, and winding. Look for bumps from misplaced handles, misaligned joins, overlaps, tiny kinks, and abrupt changes in thickness. Shared coordinates should encode a deliberate relationship rather than approximate it repeatedly.

Edit the affected source paths directly or through precise, glyph-specific coordinates. Keep those refinements authoritative: generators must preserve or explicitly consume them instead of overwriting them on the next build. Recompile and compare the changed glyph with its original reference and neighboring controls. Mechanical parallelism is useful when the design calls for it; retain justified optical correction instead of forcing every curve or stroke into one formula.

Record per-glyph visual and geometry review status and remaining work. Inspecting a control set, an alphabet row, or one member of a component family does not clear every glyph built by the same helper. User-rejected drawings remain unresolved even if they pass technical validation. A report must not prefill acceptance before the images and paths have actually been inspected.

## Surface-tension connections

Apply this treatment to modular or pixel-derived designs when the brief or reference calls for softened connections. For crisp grid-based pixel fonts, preserve discrete module boundaries and step rhythm instead; use the chosen construction mode in [pixel design](../font-pixel-design/SKILL.md). In the softened mode, keep square modules and square exposed terminals. Soften **negative space at contacts** using tangent concave fillets at inside corners. Where modules touch only diagonally, construct a restrained smooth neck between straight edges.

Do not round every outside corner or overlay circles at contacts. Circular overlays create convex knots, changing connected blocks into bubbles; reducing their radius does not fix curvature. Build the final contour's transition itself.

Check tangent direction at both endpoints: the curve must continue each adjoining edge without a kink. Inspect both diagonal orientations and three-of-four-cell intersections, not just the glyph that exposed the defect. Compare the compiled silhouette directly with the concept; a clean SVG control does not clear related joins.

Touching component contours can look correct while retaining self-intersections after build cleanup. If diagnostics persist, construct the final unified boundary explicitly and revalidate; do not assume overlap removal repaired point contacts because the preview looks filled.

## Evidence and acceptance

Run `validate_font_project` after each transactional import with the latest revision; reopen and re-evaluate conflicts. Name affected glyphs, failed invariants, and measurements. Reinspect holes, winding, baseline, extrema, accidental darkening, self-intersections, and conversion distortion in actual exported formats.

Keep SVG companions. Use PNG `pixel_scale=4` for joins/details, `3` for word-level diagnosis, and separate `1` proofs at actual small reading size. Record `font_size`, scale, revision, and font-byte hash. Split sheets that would be downscaled; enlarging an old bitmap adds no evidence.

View clean compiled images and explain whether corrections preserve negative space, weight, and identity. Distinguish generated, inspected, accepted, and unresolved cases. If visual inspection is unavailable, leave acceptance pending.
