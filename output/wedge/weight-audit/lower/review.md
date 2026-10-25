# Lowercase perceived-weight audit

Baseline revision: `c5c1dfebdde7e86a107e9b155087a50ececa2a571cbd6d86c8d50010f22c451c`
Font SHA256: `07ff25a10eb43e8bd90e5d88a2d1b63fb7a9e4abdbff6402c261c4cd50b23b7f`

All26 lowercase letters were inspected in compiled isolated display proofs, word proofs, native24px text, and actual SVG path commands. One correction is recommended and accepted by root: **d-778**, which opens the lower counter without changing the outside silhouette or prior bulge fix. The25 other letters remain unchanged.

The `d` lower-bowl section was55.83 units at SVGx287, versus22–23 in the related round controls. The selected counter changes it to approximately30.83 while keeping the stronger side and distinctive counter form. Both candidates compiled cleanly; outlines outside d, advances/bearings, cmap and GPOS are unchanged.

The retained control system is105–106 upright stems,113 round sides, approximately106–107 compensated v/w/x/y diagonals. These are reference families, not a universal target. `k`, `g`, `s`, terminal wedges and curved joins have separate optical reasons. Larger i/j dots stay106×106.

| Glyph | Decision | Visual finding |
|---|---|---|
| a | Retain | Narrowed lower bowl keeps even apparent weight with its106 stem; no excess left mass in bad/adapted. Retain current shape. |
| b | Retain | Bowl and upright balance; bottom hairline remains light, with no dark stem/bowl knot. |
| c | Retain | Open side and triangular terminal preserve contrast without appearing heavier than o/e. |
| d | d-778 counter | Current lower bowl is perceptibly darker than b/q/o in bad dad adapted paddle. Select d-778 counter-only correction: opens lower counter while keeping outer silhouette and previous bulge correction. |
| e | Retain | Counter, crossbar and left curve retain the intended high contrast; no local heavy patch in middle/successful. |
| f | Retain | Stem and hooked terminal balance the ascender family; crossbar stays visibly thin. |
| g | Retain | Two-storey construction is denser than o by design, but repeated g in rough/graphic has no isolated overweight section. Keep triangle ear and strong linking bridge from the concept. |
| h | Retain | Shared shoulder and upright weights remain coherent beside n/m. |
| i | Retain | Dot reads clearly as a separate diamond; its latest enlargement is appropriate beside stem. Preserve. |
| j | Retain | Dot matches i; descending hook retains enough body without becoming a lump in joining/joyful. |
| k | Retain | Leg appears slightly forceful but balanced beside tall stem in frisky; no correction justified. |
| l | Retain | Simple upright has the same apparent weight as h/i stems. |
| m | Retain | Three strokes produce greater total black area, but each maintains n-like color; do not lighten merely because letter is wider. |
| n | Retain | Control letter has stable upright color and shoulder tension. |
| o | Retain | Rounds have adequate compensation beside n; top/bottom remain fine and sides balanced. |
| p | Retain | Bowl color matches b; descender stays the same stem weight. |
| q | Retain | Bowl balances p/o and stem join remains clean after prior spur removal. |
| r | Retain | Faceted terminal remains assertive as in reference, while main stem matches n. No terminal reduction. |
| s | Retain | Spine appears comparable to adjacent letters in successful/stories; compact form needs its present curved weight. |
| t | Retain | Straight body and low hook balance f/r; crossbar is appropriately light. |
| u | Retain | Two upright strokes agree; bottom turn has adequate thinning and no dark join. |
| v | Retain | Recently compensated diagonal now balances n/o at display and24px. Preserve. |
| w | Retain | Repeated descending strokes retain coherent weight; center is compact but no overweight blob. Preserve latest adjustment. |
| x | Retain | Central crossing has strong but controlled color; does not require thinning because overlap is structural. |
| y | Retain | Body agrees with v; tail is visibly lighter and terminal distinctive. |
| z | Retain | Long diagonal is balanced beside x/v; terminal wedges and thin rails keep it from looking blocky. |

See `review.json` for per-glyph geometry and measurements, `paths.txt` for source commands, and `d-comparison.png` / `d-native.png` for compiled alternatives.
