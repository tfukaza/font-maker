# Super Pixel visual review

## Dotted-letter height correction — 2026-09-15

Current revision: `e1e93a6fbe9c7850195bdebd959989b7fc43865254fea8c917347c74c5800fd4`.

Raised the `i` and `j` body tops from 400 to the declared 500-unit x-height; moved their unchanged 100×100 dots from 500–600 to 600–700, retaining a 100-unit gap. The `i` baseline stays at 0 and `j` descender at −100. Advances, sidebearings, kerning, mappings, and every other compiled outline are unchanged. TTF, OTF, and WOFF2 measurements agree; validation reports only the existing unset-font-license information message.

Inspected the [before/after comparison](snap-grid/build/previews/dotted-height-fix-2026-09-15/comparison.png), guide-overlaid controls, `minimum ninja jinx` at 72px/3× and native 24px/16px, the original title words, and punctuation/f-sequence contexts. The stems now share the n/x top line instead of dropping a module below it. Dots stay separate at native sizes, the square construction and j foot are preserved, and neither `fi` nor `ij` fuses. This accepts the scoped dotted-height repair, not a new whole-font review.

The [repair report](snap-grid/build/previews/dotted-height-fix-2026-09-15/report.json) records settings, shaping, hashes, measurements, and recoverable pre-fix font/source backups. The generator now preserves this correction, with regression tests for all three export formats. Earlier evidence below belongs to the explicitly stated earlier revision and has not been relabeled as current.

## Earlier spacing and punctuation review

Reviewed font revision: `e50989f66f119603b8c51d6840e816bcc4710deb9b14e68eaeda95543a3074f7`.

This pass covered controls, uppercase and lowercase pairs, targeted words, punctuation, and numbers. Kerning was compared with ligatures held off. Large PNGs used 3× raster scale; a separate 24px specimen checked small-size legibility. Two independent reviewers inspected the proposed corrections before acceptance. The explanations below apply to the inspected samples, not every possible string.

## Accepted corrections

All values are adjustments in a 1000-unit em. Negative values bring the second glyph closer.

| Pair | Before → after | Visual reason |
| --- | --- | --- |
| `To` | −25 → −125 | The round lowercase form now sits beneath the overhang without the detached opening seen in `Tom`. |
| `Ta` | −25 → −125 | Reduces the open area below the T arm while retaining visible clearance from the a's upper bar. |
| `Te` | −25 → −125 | Brings the e's upper contour into the T's overhang; the stem channel stays open. |
| `Ty` | −45 → −125 | `Type` and `Typography` begin as coherent words; a continuous white channel separates the stems. |
| `Tr` | −20 → −125 | Removes the excess gap before the r shoulder in `Try`; the shoulder does not touch the T. |
| `Tu` | −20 → −125 | Balances the lower stem gap with the T's empty overhang area. |
| `LT` | −25 → −70 | The upper and lower open regions interleave more evenly without the L foot crowding the T stem. |
| `LY` | −25 → −70 | `LYRIC` gains a coherent opening; the Y stem remains distinct from the L foot. |
| `LV` | −25 → −50 | Modestly reduces the hollow area above the L foot without squeezing the low V. |
| `FA` | 0 → −20 | Less empty area beneath the F arm; the upper projecting bar still clears the A. |
| `PA` | 0 → −20 | Reduces the hollow region beneath the P bowl without crowding the adjacent upper forms. |
| `T.` | 0 → −140 | The period attaches to the T stem instead of floating beyond the overhang. |
| `V.` | 0 → −140 | The period is closer to the V's low point and remains a separate square. |
| `Y.` | 0 → −140 | Improves attachment to the lower stem while preserving a visible gap. |
| `F.` | 0 → −180 | Reduces the conspicuous lower-right cavity between the F stem and its punctuation. |
| `r.` | 0 → −100 | The period in `pair.` attaches to the stem rather than the distant shoulder envelope. |
| `7/` | 0 → −90 | Removes the oversized break inside `11/07/2026`; both diagonal silhouettes remain distinct. |
| `ra` | 0 → −150 | Tucks the a below the open r shoulder. `rare`, `rara`, `ratio`, `parallel`, and `Typography` no longer show a large internal cavity. The narrow shoulder gap remains visible. |
| `re` | 0 → −25 | Brings the final e in `rare` and `more` into the word's rhythm while preserving a clear shoulder channel. The −40 candidate pinched the upper gap with little benefit below. |
| `ro` | 0 → −25 | Evens the alternating ro/or rhythm in `roro`; confirmed in `robot`, `road`, `rose`, and `wrote` at display and native 24px sizes. The bowl remains distinct from the shoulder. |

`ra` was missed in the initial pass and corrected after user feedback. This prompted explicit pending/accepted/needs-change reasoning in the skill instead of blanket visual approval. An independent forward test then left `re` unresolved; comparison of 0, −25, and −40 led to the two modest final corrections above.

## Retained spacing

`AV`, `VA`, `AW`, `WA`, `AY`, and `YA` retain their existing small corrections: the stepped diagonals form open, coherent gaps in `AVATAR`, `WAYWARD`, and `WAYNE`. `AT` and `TA` retain −20 because their upper horizontal edges already approach closely while their lower shapes remain distinct. The H/n controls retain the regular stem channel. The 400-unit word space remains visibly larger than internal gaps.

`ar` retains its straight channel between the adjacent stems. `re` and `ro` need much smaller corrections than `ra` because their left edges already approach the r shoulder; copying the −150 adjustment would over-tighten that region. The decimal in `9.5` remains unchanged because both digits and the period already read as one number with distinct marks.

## Punctuation weight

Colon and semicolon dots changed from 200×200 to 100×100 units, matching the period and i dot. The semicolon's lower portion follows the comma's one-module tail. Advances changed to fit the narrower marks: colon 200, semicolon 300. `A:`, `i:`, `a;`, `n;`, `12:30`, and unspaced `a;b.` retain visible neighboring clearance. The semicolon with an explicit following space retains a normal word boundary.

## Evidence

- [Actual before/after ra comparison](snap-grid/build/previews/kerning-review/super-pixel-ra-comparison.png)
- [Actual before/after punctuation comparison](snap-grid/build/previews/kerning-review/super-pixel-punctuation-comparison.png)
- [re/ro candidate comparison](snap-grid/build/previews/kerning-review/re-ro-candidates.png)
- [ro in words](snap-grid/build/previews/kerning-review/ro-words.png)
- [re/ro native 24px check](snap-grid/build/previews/kerning-review/re-ro-small.png)
- [Final text and punctuation](snap-grid/build/previews/super-pixel-punctuation.png)
- [Native 24px check](snap-grid/build/previews/super-pixel-small.png)
- [Build report, hashes, revisions, and recoverable earlier versions](build-report.json)

The reusable skill script generates further proof sheets with pending review entries. Generation alone does not certify their visual quality. Export validation reports no errors or warnings; the remaining information message is that the designer has not selected a font license.
