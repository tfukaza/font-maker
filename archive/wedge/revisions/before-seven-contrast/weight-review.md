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
