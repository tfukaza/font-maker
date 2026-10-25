"""Refresh delivery documentation and record the visual review decisions."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
revision=json.loads((p/'build-report.json').read_text())['revision']
old=(p/'README.md').read_text()
metrics=old[old.index('## Coordinate and construction record'):old.index('## What the trial exercised')]
readme='''# Party Blob

An original experimental display font inspired by the supplied “Snap Engine / Super Rec” lettering: swelling bowls, thin joins, off-center counters, bulb terminals, and deep tails. This is a usable Latin prototype with the standard character inventory, intended for large display text.

## Open and use

- `specimen.html`: portable interactive tester with embedded WOFF2 and reference image. Open in a browser; no network dependencies.
- `character-specimen.png` / `.svg`: full inventory drawn from the actual exported TTF.
- `specimen.png` / `.svg`: the two reference lines, composed from compiled outlines.
- `font/build/fonts/PartyBlob-Regular.ttf`: installable TrueType.
- `font/build/fonts/PartyBlob-Regular.otf`: OpenType/CFF.
- `font/build/fonts/PartyBlob-Regular.woff2`: webfont.
- `font/font.yaml`, `font/glyph-template.svg`, and `font/glyphs/`: durable editable Font Maker project.
- `draw_glyphs.py`, `extend_glyphs.py`, and `drawings/`: original source drawings.
- `concepts/ligature-exploration.png`: AI concept board; `concepts/prompt.txt` preserves its prompt.

Enable discretionary ligatures (`dlig`) for the optional swash **En**: `font-feature-settings: "kern" 1, "dlig" 1;`. Standard `liga` has no substitutions configured. The tester provides independent kerning and En controls.

## Inventory and provenance

- **103 encoded characters**: uppercase A–Z, lowercase a–z, digits 0–9, every printable ASCII symbol and space (95 total), plus **– — ‘ ’ “ ” • …**.
- One unencoded `E_n` discretionary ligature: **104 authored glyphs** total.
- Compiler control glyphs bring the export counts to 107 in TTF/WOFF2 and 105 in OTF.
- Original Bézier geometry throughout. No installed font outlines, automatic tracing, or generated raster shapes were imported as font outlines. The new symbols include quadratic segments, converted exactly to cubic curves on import.
- The optional AI exploration used the built-in image-generation tool with the current compiled Party Blob specimen as a style reference. It produced six raster concepts for `na`, `in`, and `ec`; none is an active substitution.
- No distribution license has been selected. Final validation reports only informational `FONT_LICENSE_UNSET`.

## Kerning and creative ligatures

Fourteen reviewed pair exceptions are configured: AV −170, Re −25, Sn −60, up −95, Pa −180, Po −130, Ta −160, To −160, Te −150, Va −110, Wa −90, Ya −150, Fa −100, Fo −80.

The final comparisons in `final-kerning/` show improved rhythm in “Party Blob,” “Tea Today,” “Vase Wave,” and “Yarn Foam Fair.” Pa is already snug; additional tightening would risk contact. `ra` has a tight upper terminal and a large lower cavity, so simply tightening it would not solve the drawing relationship.

Creative candidates are documented in `layout-review/REVIEW.md`. A treatment that changes perceived letter identity—such as `nn` resembling `m`, removing a distinguishing dot, or extreme kerning that fuses letters—requires user consultation unless full creative freedom was explicitly granted. Optional `dlig` status does not waive that consultation. No such new treatment has been enabled.

'''+metrics+'''## Repository trial and fixes

The actual `fontmaker-mcp` stdio server was exercised through `mcp.ClientSession`, with calls and responses retained in `mcp-transcript.jsonl`. Work covered doctor, project creation/opening, shared metrics, SVG batch import, validation and temporary compilation, spacing suggestions/application, kerning, discretionary substitution, HarfBuzz shaping, PNG/SVG previews, and TTF/OTF/WOFF2 export. Server restarts exercised durable state recovery.

Applied repo skills: font-production-workflow, font-design-metrics, font-outline-qa, font-spacing-kerning, font-ligature-design, and font-specimen-review. Independent read-only visual reviews covered the new capitals, mixed text, figures, and symbols.

Four defects found and fixed:

1. **Template height:** templates now accommodate the complete ascender-to-descender span instead of clipping deep descender guides to a UPM-square canvas.
2. **Spacing proposal rounding:** advance widths are reconciled with source outline width while preserving proposed sidebearings. This prevents an otherwise inconsistent proposal from invalidating the font.
3. **FontForge UPM:** ascent/descent are assigned before EM so a 1070-unit vertical span does not silently change the requested 1000 UPM.
4. **Quadratic SVG import:** SVG Q/T curves are elevated exactly to cubic Béziers before replay into FontForge's cubic layer, avoiding the “qCurveTo only applies to quadratic fonts” build error. A regression compiles all three formats and checks actual outline bounds.

Visual review additionally caught and corrected a filled `9` counter, opposing dollar-sign stroke winding, W's excessive rightbearing, light dashes, low colon dots, and initial capital–lowercase spacing. These required image inspection; numeric validation alone did not identify them.

## Skill improvements

- **font-production-workflow:** a deliverable Latin prototype defaults to all 103 characters above unless the user explicitly asks for a smaller study or a different script. Verify both exported cmap coverage and shaping; early control glyph studies remain useful but do not fulfill the final inventory.
- **font-ligature-design:** explore expressive combinations from this font's actual gestures, optionally use AI concepts, preserve ordinary rendering, redraw original vector geometry, and prove the actual substitution inventory in words. Consult on changes to perceived letter identity unless explicitly authorized.
- **font-spacing-kerning:** distinguish positioning problems from drawing interactions; image concepts cannot establish numerical spacing; hold ligature features fixed when checking replacement boundaries. Apply the same consultation rule to extreme positioning that changes perceived text.
- **font-specimen-review:** review the complete intended inventory and actual configured ligatures; generic f-sequence proofs cannot certify an unrelated En ligature.

## Acceptance evidence

- Final source revision: `REVISION`.
- Backend: FontForge `20251009`.
- Full Python suite: **46 passed**. Ruff passed; Mypy passed for all 13 source files.
- All four edited skills passed `quick_validate.py`.
- Final project validation: no warnings/errors; only the informational license diagnostic.
- Every export: artifact hash and family name verified, 1000 UPM, ascender 800 / descender −270, cap 720 / x-height 420, all 103 encoded characters mapped and shaped without `.notdef` with features off and on.
- `En Engine`: dlig substitutes exactly two `E_n` glyphs in TTF, OTF, and decompressed WOFF2.
- `AV Re Sn up`: kerning preserves glyph names/clusters and reduces advance by exactly 350 units.
- Standard f-sequence sentence: feature comparison has identical shaping because no standard ligatures are configured.
- Compiled visual review: inventory sheet; capital/lowercase rows; digits including I/l/1 and O/0; punctuation in boundaries, time and currency strings; reference words; final kerning OFF/ON sheets at 96 px, scale 3; reference detail at 160 px and a small 32 px raster.
- Browser: the embedded font visibly loads and the updated tester supports capitals, figures, and symbols; feature toggles and unsupported-accent feedback were checked.

`build-report.json` and `acceptance.json` identify the delivered artifacts. Older proof JSONs and transcript entries retain intermediate revisions and failures as evidence; they do not replace the final build report.

## Prototype limits

The reference's most expressive rhythm appears in S, p, R and En. Other combinations remain separate reusable forms. Hairlines are fragile at 32 px; use larger sizes for this prototype. Further optical polish (especially B/D corners), a broader kerning corpus, accents and language coverage, and production hinting remain future work. The font name and all exported family/PostScript names are Party Blob; historical logs retain an earlier working name.
'''
(p/'README.md').write_text(readme.replace('REVISION',revision))
notes='''# Party Blob — kerning and ligature review

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

At final revision REVISION, the dollar slash winding matches its body and compiles to continuous ink. En/em dashes increased from 39 to 60 units; colon/semicolon upper dots were raised, with a modest lower-colon raise. T pairs were tightened by another 40 units; Pa stayed unchanged. The regenerated refinement proof and full compiled inventory sheet were visually inspected.

## Final kerning decision

All five `../final-kerning/sheet-*.png` files were inspected with kerning off/on and ligature features fixed off. “Party Blob,” “Tea Today,” “Vase Wave,” and both parts of “Yarn Foam Fair” have cleaner rhythm without unwanted contact. Accepted for this display prototype. This focused pass is not an exhaustive kerning corpus or a small-text suitability claim.
'''
(p/'layout-review/REVIEW.md').write_text(notes.replace('REVISION',revision))
index_path=p/'final-kerning/index.json'
index=json.loads(index_path.read_text())
observations=[
'Pa closes an excessive gap; bowl and a terminal remain narrowly separated. Do not tighten further.',
'Te and To move under the crossbar without touching; word boundaries remain clear.',
'Va and Wa reduce diagonal white space with recognizable independent letters.',
'Ya and Fo close broad open gaps while keeping terminals and bowls distinct.',
'Fa improves the final split word; its top bar retains clear separation from a.'
]
for case, note in zip(index['cases'],observations):
 case.update(review_status='accepted',observation=note,why_acceptable='Compiled OFF/ON image inspected; improved display rhythm without an accidental collision.')
index['counts']['pending']=0
index['counts']['accepted']=len(index['cases'])
index['review_note']='All five rendered sheets visually inspected. Acceptance is limited to these words at these settings.'
index_path.write_text(json.dumps(index,indent=2))
print(revision)

# Apply the accepted creative-ligature delivery notes when that build exists.
if (p/'creative-acceptance.json').exists():
 import runpy
 runpy.run_path(str(p/'update_creative_docs.py'),run_name='__main__')
