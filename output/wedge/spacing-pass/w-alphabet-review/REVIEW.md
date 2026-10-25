# Hakiland Display: W permutation review

Snapshot: `baseline.ttf` copied from the named Hakiland Display TTF before this refinement. The immutable hash is recorded in `pairs.json`. The four sheets render every ordered pair of W with A–Z/a–z (103 unique pairs, including WW) through HarfBuzz with the existing kerning enabled. Every panel contains a 100 px pair and a 28 px `nn<pair>nn` context. All 103 panels were visually inspected in the four PNGs; this is a baseline review, not acceptance of revised values.

## Principal finding

`We` is not an isolated exception. The open wedge on W's right side creates a recurrent excess of white space beside many x-height letters. The existing −45 for `We/Wc/Wg/Wo` is visibly insufficient. `Wd/Wq` are related omission candidates at zero; their geometry differs from e/o, so trial them separately. The adjusted a is also a separate proof case. A small fixed list overlooked other low shoulders and direction-specific differences.

## Priority for refinement

| Direction / pairs | Baseline observation | Suggested action |
| --- | --- | --- |
| `We Wc Wo Wg` | Clearly loose. The triangular interval is larger than adjacent lower-case rhythm at both sizes. | Trial stronger negative kerning in this family; inspect each actual outline and words. |
| `Wa Wd Wq Ws` | Related low/round forms; Wa/Ws already −45, Wd/Wq zero. Wd's ascending right side and q's lower terminal are exceptions worth checking. | Trial tightening independently; do not equate all bowls mechanically. |
| `Wm Wn Wp Wr Wu` | Low shoulder/stem neighbors are loose underneath the right W diagonal; existing Wr/Wu −12 has little effect. | Add to the review queue for negative trials. |
| `Wv Ww Wx Wy Wz` | Low diagonal/flat neighbors leave a wide interval; these were absent from the existing list. | Negative trials at display and reading sizes, checking serifs and points. |
| `Wi Wj Wf Wt` | Open at x-height but taller dots/ascenders/crossbars limit how much nesting is possible. | Individual modest trials; inspect actual nearest approach before using any lowercase group. |
| `WC WG WO WQ WS` | Round cap neighbors are more open than the stem-cap controls. | Secondary negative trials, distinctly smaller/different from lowercase if top clearances demand it. |
| `WX` | Opposed diagonals make the middle interval look wide while top serifs constrain movement. | Secondary independent trial; do not borrow round-cap or lowercase values. |

## Reversed pairs and controls

- `eW cW oW gW` are much less loose than `We Wc Wo Wg`. The heavy left diagonal of W and the rightmost letter shapes change the visual interval. There is no basis for mirroring forward values automatically.
- `fW` and `rW` already have close upper/middle detail (f terminal and r diamond toward W's left stroke). Any mirrored large negative kerning risks crowding or collision. Retain current values unless separate trials show an improvement.
- `AW/WA` and `LW` already have meaningful adjustments and look coherent in these baseline proofs. A further change is not established by this review.
- `WW`, `WT/TW`, and W with cap stems are limited by the top wedges. Their wide triangular white areas do not justify inheriting lowercase adjustments.
- Remaining reverse lowercase pairs, including `aW bW dW hW iW jW kW lW mW nW pW qW sW tW uW vW wW xW yW zW`, show no conspicuous baseline defect requiring the same fix as `We` in these two-size proofs. This does not establish an exact preferred value for each or replace words/acronym context.
- Remaining cap pairs were also inspected; no broad cap-stem correction is indicated. Avoid changing W's sidebearings globally because it would disturb satisfactory cap/stem and reversed pairs.

## Scope limits

No font, glyph outline, spacing manifest, or project metadata was changed. These proofs generate candidate pairs and identify collision risks; final trial values must be rendered from the rebuilt font and reviewed, with coverage tied to that font hash/revision. No punctuation or digit permutations were included in this bounded alphabet review.
