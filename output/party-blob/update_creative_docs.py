"""Update the delivery notes after the creative-ligature build."""
import json,re
from pathlib import Path
p=Path(__file__).resolve().parent
revision=json.loads((p/'build-report.json').read_text())['revision']
f=p/'README.md';s=f.read_text()
s=s.replace('One unencoded `E_n` discretionary ligature: **104 authored glyphs** total.','Six unencoded discretionary ligatures: `E_n`, `e_c`, `i_n`, `n_a`, `o_o`, `r_t`: **109 authored glyphs** total.')
s=s.replace('107 in TTF/WOFF2 and 105 in OTF','112 in TTF/WOFF2 and 110 in OTF')
s=s.replace('Enable discretionary ligatures (`dlig`) for the optional swash **En**:', 'Enable discretionary ligatures (`dlig`) for **En, ec, in, na, oo, rt**:')
s=s.replace('independent kerning and En controls','independent kerning and creative-ligature controls, targeted sample buttons, and separate on/off comparisons')
s=s.replace('It produced six raster concepts for `na`, `in`, and `ec`; none is an active substitution.','It produced concept boards for `na/in/ec` and `oo/rt`. Ideas informed original vector drawings; no generated pixels were traced or imported. Prompts and images are saved in `concepts/`.')
s=s.replace('Fourteen reviewed pair exceptions are configured:', 'Fourteen original pair exceptions are configured:')
s=s.replace('Creative candidates are documented in `layout-review/REVIEW.md`.', 'The five new ligatures and six added exterior kerning pairs are documented in `ligature-proofs/REVIEW.md`. A separate review font and pre-ligature baseline remain in `ligature-review/`.')
s=s.replace('**46 passed**','**47 passed**')
s=re.sub(r'Final source revision: `[0-9a-f]+`',f'Final source revision: `{revision}`',s)
s=s.replace('The reference\'s most expressive rhythm appears in S, p, R and En. Other combinations remain separate reusable forms.', 'The reference\'s expressive rhythm now extends through the flowing ec/in and the nested na/oo/rt. Turning dlig off restores the original independent forms.')
section='''## Creative ligatures — delivered

All five planned candidates were promoted after compiled review. The font now has six optional dlig substitutions, including the unchanged En.

| Pair | Final drawing | Proof words |
| --- | --- | --- |
| ec | Shared lower sweep with open upper channel | Rec, record, collect |
| in | Continuous i hook into n; separate tilted dot | Engine, spinning, inside |
| na | Re-carved n exit nested beside a, with widened white seam | Snap, banana, natural |
| oo | Original first o and a complementary curved left side on the second | moon, balloon, groovy |
| rt | Lowered r bulb under a short rounded t crossbar | Party, started, artwork |

`ligature-proof.png` / `.svg` compare the compiled ordinary pairs, replacements, and words. `ligature-proofs/` contains equal-size current / kerning-only / ligature comparisons, 96 px word sheets, 160 px detail, actual 32 px rasters, repeats, punctuation boundaries, and targeted kerning cases. These are script-generated proofs from actual font bytes, not AI mockups.

The six new exterior kern pairs preserve existing component spacing: R/e_c −25, S/n_a −60, F/o_o −80, P/o_o −130, T/o_o −160, T/e_c −150. Earlier generic boundary sheets show identical kern-off/on results because their text does not trigger any pair rules. `kerning-active-1.png` and `kerning-active-2.png` use real affected words and print the measured change; those are the meaningful kerning demonstrations.

`creative-acceptance.json` verifies 33 strings in all three formats with dlig off/on, exact glyph names and clusters, all 103 mappings, and unchanged original compiled outlines and metrics. In particular, final → f + i_n + a + l; banana → b + a + n_a + n_a; Engine → E_n + g + i_n + e. Feature-off shaping exactly matches the saved baseline. No nn→m, dot removal, infinity-like oo, or other identity-changing treatment is enabled.

Reproduce with `draw_ligatures.py`, `mcp_workflow.py` using `promote-ligatures.json` and `rebuild.json`, `proof_ligatures.py font ligature-proofs`, and `verify_ligatures.py font creative-acceptance.json` (use paths relative to the current working directory). `package_proof.py` rebuilds the tester and inventory sheets; `create_archive.py` refreshes the ZIP.

'''
if '## Creative ligatures — delivered' not in s:s=s.replace('## Prototype limits',section+'## Prototype limits')
f.write_text(s)
report='''# Creative ligature visual acceptance

Final delivered revision: REVISION. Review-font final geometry: a8eced687c967935e75dc99061346771214593015b0b87fb6a3198a4e245a5d4.

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
'''
(p/'ligature-proofs/REVIEW.md').write_text(report.replace('REVISION',revision))
print(revision)
