# W family trial review

All 103 ordered W/alphabet pairs were rendered again from `trial.ttf` and visually inspected in `sheet-1.png` through `sheet-4.png`: 100 px pair plus 28 px `nn<pair>nn` context. This review uses the compiled outlines and HarfBuzz positioning. The immutable font hash and every observed kerning value are in `pairs.json`.

The 26 changed forward pairs pass this matrix review: none has a visible collision or over-tight appearance at these two sizes. Their revised spacing is more coherent than the baseline. This is supporting evidence for accepting the candidate values, subject to the root agent's separate word proofs and final production rebuild verification.

| Pairs | Trial value | Finding |
| --- | --- | --- |
| `Wa Wc Wd We Wg Wo Wq` | −110 | Considerably improves the loose interval. We/Wc/Wo nest naturally beneath the diagonal. Wd's high stem, g's ear, and q's bowl remain separate. No pair appears pinched in the small context. |
| `Ws` | −90 | The serpentine edge is appropriately a little farther out than the round group. Clear and balanced at both sizes. |
| `Wm Wn Wp Wr Wu` | −80 | Low shoulders now follow W more naturally. Wr's diamond remains separate; Wp has adequate upper serif clearance. The rhythm is noticeably improved without appearing stuck to W. |
| `Wi Wj` | −65 | Both diamonds remain visibly separated from W's top/right diagonal. Small-size dots stay distinct. Their tall marks correctly limit the adjustment relative to low rounds. |
| `Wv Ww Wx Wy Wz` | −65 | Diagonal/flat neighbors improve, with clear upper terminals and no false touching at 28 px. Their somewhat lighter nesting than rounds is justified by the top points/serifs. |
| `Wt` | −35 | Top/crossbar stays separate. It retains a little more air than x-height neighbors, consistent with its taller form; no further change is indicated by these proofs. |
| `WC WG WO WQ WS` | −35 | Mild tightening improves cap-round rhythm. Cap overshoots, G's interior bar, and Q's tail remain separate. None is crowded against W at the top. |

The remaining 77 pairs retain their baseline advances. Both visual inspection and measured shaping confirm that reversals did not inherit the new forward kerning. In particular fW/rW remain safe; WW and WT/TW retain top-wedge clearance. Wf at zero remains reasonable because the high bulb limits nesting. WX was deliberately retained at zero; its top wedges limit tightening, and no change is required for this pass.

Scope: alphabet matrix only, two sizes. Words and punctuation are outside this agent's trial review. No font or source files were modified.
