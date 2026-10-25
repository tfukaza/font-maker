# Hakiland Display — design consistency, version 0.114

Reviewed all 103 encoded characters against the concept art, related construction families, source SVG geometry, and fresh compiled display/native 24 px proofs. Three subagents covered capitals, lowercase, and figures/punctuation; the integrator checked mixed families and the final exports.

| Glyphs | Refined relationship |
| --- | --- |
| E F L N Y | Attached straight-stem serif cuts now follow the shared 45° family. |
| f | Foot flares match related upright lowercase stems. |
| u | Head wedges match n/i/j; exit wedge follows d. |
| 1 and 4 | Figure foot cuts match upright serif angles. The broad flat top of 4 meets cap height; its diagonal remains parallel. |
| 7 | Fine upper stroke grows smoothly toward a fuller base, with a much thinner top bar. This implements the user's suggestion to use 4's contrast and a thicker lower stroke. |

The 7 is a new construction rather than another uniformly thinner band. Three constant-width and three tapered alternatives were compared. T2 was selected: its inner cubic is monotonic, without an inflection or bulge, and starts tangent to the outer-edge direction before gradually diverging. This deliberate taper takes precedence over the earlier general preference for parallel edges. Prior weight-review acceptance of the uniform 7 is superseded.

The other 93 characters retain their exported outlines. Distinct bowls, arm terminals, Q/R tails, and optical overshoots were reviewed and preserved instead of being forced into identical geometry.

[7 before/after](seven-taper-comparison.png) · [Full comparison](consistency-comparison-80.png) · [Native 24 px](consistency-comparison-24.png) · [Per-glyph evidence and measurements](consistency-review.json)

TTF, OTF, and WOFF2 pass coverage and tested-context shaping checks. Advances, kerning, and substitution tables remain unchanged. The u outline extends one unit farther left (LSB26→25), and its exit reaches five units farther right; context spacing was reinspected. Other outline changes are confined to the ten listed glyphs. User aesthetic judgment remains open.

The design metrics and serif skills now encourage creative redistribution of weight—light entries, stronger terminals, relieved joins and tapers—when constant-width adjustments fail, with compiled comparisons and explicit geometry checks.
