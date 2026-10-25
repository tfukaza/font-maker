# Hakiland Display — perceived stroke weight, version 0.113

All 103 encoded characters were reviewed by construction family, through the actual SVG paths and compiled specimens at display and native 24 px. Three subagents covered capitals, lowercase, and punctuation; the main pass covered all ten figures, compared proposed changes, and integrated the exports.

| Changed family | Correction | Preserved |
| --- | --- | --- |
| 7 | Long diagonal about 132→108 units perpendicular to its edges; top bar 109→92 | Parallel slope, 45° wedge, outer bounds, advance |
| S and $ | Central band about 143→129 units | Terminals, extrema, dollar bar, spacing |
| d | Lower bowl thickness about 56→31 units at the reviewed section | Outer silhouette and previous bulge repair |
| . , : ; ! ? … | Diamond/head size 78→92 units | Shared 45° cuts, baseline and advances |

The other 92 entries were retained. In particular, the recent w/diagonal compensation and larger i/j dots remain appropriate. Weight varies deliberately between upright, curved, diagonal, thick, and hairline families; the pass does not force equal geometry.

Before/after evidence: [display comparison](weight-comparison-72.png), [native 24 px comparison](weight-comparison-24.png), [complete per-glyph record](weight-review.json). Full diagnostic/trial proofs are under weight-audit/ in the workspace.

TTF, OTF and WOFF2 compile and shape the tested contexts. Coverage, all advances, kerning and substitution tables are unchanged. Only the 11 selected outlines changed. The previous 0.112 geometry review did not catch the optical-weight issues above and is superseded for those glyphs. The revised drawings remain subject to the user's aesthetic judgment.

The font metrics and serif skills now direct reviewers to audit every delivered construction family, including figures and symbols, and consider lightening as well as thickening strokes.

---

## Previous pass (version 0.112)

# Hakiland Display — second review pass

Version 0.112 preserves all 103 encoded characters and the existing glyph drawings.

Three subagents independently reviewed letter design, kerning and ligature need. The main review covered figures, marks, spaces, cross-review and integration.

- All 52 letters and 51 remaining characters were inspected visually and through their authored SVG paths. No further contour correction was warranted.
- The kerning pass inspected 732 unique ordered pairs around A, T, V, Y, F, L against Latin letters and 12 punctuation marks in both directions. It refined 223 pairs, with compiled pair, context, word and 24 px native proofs.
- A ligature review found no demonstrated benefit in the tested f-family, Q-tail, r-diamond, crossbar, shoulder and diagonal candidates. Separate glyphs remain active. Four positive 24-unit adjustments to fb/fh/fk/fl give their upper terminals room.
- TTF, OTF and WOFF2 shaping checks confirm all 227 adjustments. Outline, advance and substitution tables are unchanged. Prior W spacing checks still match.

This is a bounded review of the stated inventory, not an exhaustive claim for all possible character combinations. Detailed measurements and version/hash provenance are in second-pass-review.json. Full proof sheets remain in the Font Maker workspace under review-pass-2/.
