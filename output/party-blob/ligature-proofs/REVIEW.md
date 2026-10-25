# Creative ligature visual acceptance

Final delivered revision: 0160db525812d5fa5000d5d51bca1dda700b21b92abddb9691ef1b22939451bf. Review-font final geometry: a8eced687c967935e75dc99061346771214593015b0b87fb6a3198a4e245a5d4.

## Decisions

- **ec accepted:** e counter and c mouth stay open. The shared lower curve creates a continuous sweep; initial upper contact was redrawn into a clear channel.
- **in accepted:** i dot is retained and the hook-to-shoulder curve reads as in, including inside/spinning/final. Existing En is unchanged; Engine activates both En and in.
- **na accepted:** nested exit improves repeated banana rhythm. A 20-unit increase before a opened the lower white seam for small-size rendering.
- **oo accepted after redraw:** the first draft flattened the first o and added little beyond kerning. Final geometry preserves that o and carves the second's left side around it. Both counters and the curved separation remain open; a final 20-unit clearance increase protects the narrowest region.
- **rt accepted after redraw:** an initial collision and later pointed overhang were rejected. Final construction uses a short rounded t terminal above a lowered r bulb, with an additional 15-unit clearance adjustment. It retains r and t identities without an accent-like spur.

Two independent read-only reviews assessed word rhythm and outline/readability. The integrating agent reviewed every final construction through the overview, all punctuation/repeat boundaries, and the revised oo/rt at 160 px scale4 and actual32 px scale1. Other pairs were reviewed at those sizes by the independent reviewers. At 32 px, this display font's fine strokes remain delicate; no small-body-text suitability is claimed.

## Proof interpretation

- `*-construction`: actual compiled letters; current arrangement / a labelled kerning-only adjustment / dlig replacement, equal160px size, scale3.
- `*-words`: actual96px, scale3; dlig off/on while kern stays on.
- `*-detail`: actual160px, scale4.
- `*-small`: actual32px, scale1, without enlargement.
- `*-boundaries`: dlig fixed on, kern off/on. These generic strings do not exercise configured kern pairs, so identical rows are expected; use them only as boundary evidence.
- `kerning-active-*`: dlig fixed on, real affected words, with exact width delta printed. Rec −25, Snap −60, Food −80, Pool −130, Tool −160, Tech −150 font units.
- `overlaps`: final, banana, Engine; exact substitutions verified independently in creative-acceptance.json.

All PNG/SVG proof artwork is rendered by `proof_ligatures.py` from FontForge-built font bytes shaped by HarfBuzz. Current versus kerning-only comparisons alter placement only, never glyph geometry. AI images exist only in the separately labelled concept boards.

## AI provenance and creative boundary

Built-in image generation produced `../concepts/oo-rt-exploration.png` from the compiled character-specimen.png reference. Its exact prompt is `../concepts/oo-rt-prompt.txt`. Existing `../concepts/ligature-exploration.png` and prompt.txt supplied na/in/ec inspiration. The generated oo resembling Po was rejected. No raster outline was traced.

The user approved the five mixed flow/nesting designs while explicitly retaining consultation for letter-identity changes. No such identity-changing treatment was needed or promoted. No candidates remain pending in the delivered batch.
