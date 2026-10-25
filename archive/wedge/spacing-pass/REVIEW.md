# Wedge spacing pass

The accepted proposal is `../spacing-refinement.json`: a advances 562 → 547 with LSB 75 → 60, and 85 exact kerning values are added or revised. The matched 15-unit shift and advance reduction preserve a's right spacing while improving nanan/parallel after the bowl narrowing. H/O, n/o and space keep their advances.

Capital wedges and overhangs are the largest corrections (AV −95, AT −90, TA −95, LT −100); mixed-case T/V/W/Y pairs use separately reviewed values. Lower diagonal-round pairs receive small corrections. The existing ra/re/ro −18 stays: its top shoulder is already close, and tightening the lower cavity more would damage that relationship. Punctuation after overhangs moves closer; colon/semicolon geometry and spacing are unchanged.

Final exact-pair rows (85 pairs), word controls and actual 22px reading-size samples were all opened and visually inspected after the latest source outlines. All tested pairs remain recognizable, words remain distinct, and the corrected gaps are related to neighboring gaps rather than made numerically equal. Final ledgers contain source revision, font hash, feature maps, images, shaping and per-row acceptance notes. Approximate same-height outline clearances in `pair-clearances.json` support the review but are not aesthetic verdicts.

- `final-pairs/index.json`: 15 accepted rows, 7 inspected sheets, 50px / 3×.
- `final-words/index.json`: 14 accepted rows, 7 inspected sheets, 44px / 3×.
- `final-reading/index.json`: 6 accepted rows, 2 inspected sheets, 22px / 1×.

Scope is bounded to those strings; this does not certify every possible glyph combination. Baseline and earlier trial proofs are retained for comparison and are superseded by the final ledgers.
