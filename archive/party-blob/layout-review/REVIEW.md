# Party Blob — kerning and ligature review

## Initial focused exploration

All six `layout-review/sheet-*.png` images were inspected at source revision a11e6cc5cbf2, 96 px / scale 3. This was the earlier 40-character subset, preserved for provenance.

| Candidate | Observation and decision |
| --- | --- |
| ra | Upper terminals already tight while lower white cavity remains open. Do not solve by blindly reducing advance; drawing exploration would be more appropriate. |
| na | Baseline exit and a's upper opening could participate in a coordinated sweep. Keep as exploratory artwork. |
| in | i's hook could flow into n, but retain a distinct dot and readable two-letter rhythm. Concept only. |
| ec | Neighboring rounded masses could share an exit sweep. Most promising AI direction; still needs original drawing and actual font proofs. |
| Re, up | Existing exceptions preserve recognizable shapes and improve the reference words. Retain. |

The sheet generator holds dlig off: its “Snap Engine” comparison does not prove the E_n replacement's boundaries. Separate `En-preview-False.json` and `En-preview-True.json` prove the actual configured substitution.

## AI concepts and user consultation

`../concepts/ligature-exploration.png` contains six built-in image-generation concepts: FLOW / INTERLOCK for na, in, ec. `prompt.txt` preserves the input request; the reference was a compiled Party Blob specimen. All are raster sketches, not spacing measurements or font artwork.

FLOW ec offers the clearest coordinated sweep. FLOW in suggests a useful hook. The more fused in variant weakens component clarity and would require consultation before enabling. Some na outputs remain separate despite the prompt, demonstrating why generated lettering must be inspected rather than treated as implementation evidence.

The user specifically required consultation for identity-changing treatments, for example nn resembling m, unless full creative freedom is explicitly granted. No new substitutions from this board were enabled. A later proposal should show the exact input, ordinary and proposed rendering in words, feature/default behavior, and readability tradeoff before requesting a decision.

## Expanded inventory review and corrections

Two independent read-only reviews inspected the new capitals/mixed text and the digits/symbols at revision 5c3d5c275426. Capital forms were readable and coherent; B/D's lower-left corners were noted as optional polish. A real dollar-sign overlap defect was found. Digits and symbol counters were otherwise open, and I/l/1 plus O/0 were distinguishable.

At final revision b25f8517cf42164f8a01aa9a42168e95d142284f816544a7bdaf7835ff421050, the dollar slash winding matches its body and compiles to continuous ink. En/em dashes increased from 39 to 60 units; colon/semicolon upper dots were raised, with a modest lower-colon raise. T pairs were tightened by another 40 units; Pa stayed unchanged. The regenerated refinement proof and full compiled inventory sheet were visually inspected.

## Final kerning decision

All five `../final-kerning/sheet-*.png` files were inspected with kerning off/on and ligature features fixed off. “Party Blob,” “Tea Today,” “Vase Wave,” and both parts of “Yarn Foam Fair” have cleaner rhythm without unwanted contact. Accepted for this display prototype. This focused pass is not an exhaustive kerning corpus or a small-text suitability claim.
