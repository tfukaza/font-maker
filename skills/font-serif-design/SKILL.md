---
name: font-serif-design
description: Draw or refine original serif glyphs, including contrast, stress, serif and terminal families, bowls, joins, and optical weight. Use for serif-specific shape design and reference fidelity; not for export-only or spacing-only work.
---

# Serif Font Design

Use this skill for serif-specific drawing decisions. Keep provenance, coordinates, coverage, and delivery in the [production workflow](../font-production-workflow/SKILL.md); use [design metrics](../font-design-metrics/SKILL.md) for shared measurements and [outline QA](../font-outline-qa/SKILL.md) for every glyph's visual and SVG review.

## Identify the design's construction

Read the concept as a connected system: proportions, contrast, stress, serif shape, bracket treatment, terminal vocabulary, and characteristic counters. Distinguish wedge, slab, hairline, bracketed, and other treatments from the actual brief; do not impose one subtype's geometry on the others.

Record a few approved controls for stems, rounds, diagonal letters, and serif attachments before expanding the alphabet. Where a reference exists, identify the structures that make it recognizable, including the bowl construction of `a/d`, the form of `g`, and the gesture of `Q/R`. Simplification should retain those relationships and the user's approved changes.

## Resolve strokes, serifs, and joins together

Define thick and thin stroke families and how the contrast moves around a bowl. Stress need not be vertical, and contrast need not be uniform across capitals and lowercase. Compare weight through transitions, not just at the widest and narrowest points.

Use stroke modulation creatively when a form remains optically awkward. A taper toward a fuller lower stroke, a lighter entry, or redistributed weight around a join may fit the family better than one constant width. Take the contrast logic of a related form as a starting point, then compare compiled alternatives using the [weight-distribution guidance](../font-design-metrics/SKILL.md#design-the-distribution-of-weight). Keep the selected variation intentional in both silhouette and SVG geometry.

Treat serif reach, thickness, angle, and bracketing as related families. Inspect head versus foot serifs, bilateral versus one-sided attachments, and the interior space around neighboring stems. Similar serifs may need different dimensions when their attachment or context changes. Do not paste one serif everywhere and accept crowded junctions as stylistic consistency.

Measure diagonal thickness perpendicular to its edges and compare letters, figures, and symbols with the appropriate upright and round controls. Diagonals can need more or less weight; use the [perceived-weight audit](../font-design-metrics/SKILL.md#audit-perceived-stroke-weight) to decide and record compensation while preserving hairlines. Keep joins from darkening as diagonals converge, and preserve intended parallel edges where the design uses them. Neither one fixed slope nor one thickening percentage belongs to every serif design.

## Control bowls and transitions

Compare outer silhouette, counter, stem attachment, and distribution of width separately. A bowl that bulges too far sideways may need a changed outer extremum, counter placement, or handle direction; global horizontal scaling usually disturbs other relationships. Inspect `a/d/b/p/q` as related but distinct constructions rather than reflected copies or identical ellipses.

At each curved-to-straight or curved-to-curved join, inspect actual SVG endpoints and handles for the intended tangent and rate of curvature change. Smooth tangency alone does not prevent a swollen shoulder or pinched counter. Adjust the few controlling points that create the shape, then inspect the compiled contour for kinks or flat spots.

Use optical overshoot for rounds or points where the compiled comparison supports it. Thin terminals, pointed serifs, and broad flat edges do not necessarily appear aligned at identical coordinates; keep justified corrections within the recorded metric families.

## Keep details intentional and legible

Give dots, ears, tails, terminals, and punctuation sufficient visual mass for their role. Compare `i/j` dots with body weight and clearance; matching a stem's bounding width does not guarantee the dot reads strongly enough. Review light hairlines and small counters at the intended reading size, not only in large specimens.

Shape `Q` tails and other expressive details as designed continuations of the font's contrast and terminal vocabulary. Check the bowl connection, interior counter, exit angle, and neighboring baseline rhythm. Avoid both an arbitrary attached slash and unnecessary ornament when neither fits the concept.

After shape revisions, recheck words against the original concept and approved controls. Serif reach changes the apparent interletter gap; route bearing and pair changes through [spacing and kerning](../font-spacing-kerning/SKILL.md) after the revised shapes are stable.
