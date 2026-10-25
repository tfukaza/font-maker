# Party Blob

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

Enable discretionary ligatures (`dlig`) for **En, ec, in, na, oo, rt**: `font-feature-settings: "kern" 1, "dlig" 1;`. Standard `liga` has no substitutions configured. The tester provides independent kerning and creative-ligature controls, targeted sample buttons, and separate on/off comparisons.

## Inventory and provenance

- **103 encoded characters**: uppercase A–Z, lowercase a–z, digits 0–9, every printable ASCII symbol and space (95 total), plus **– — ‘ ’ “ ” • …**.
- Six unencoded discretionary ligatures: `E_n`, `e_c`, `i_n`, `n_a`, `o_o`, `r_t`: **109 authored glyphs** total.
- Compiler control glyphs bring the export counts to 112 in TTF/WOFF2 and 110 in OTF.
- Original Bézier geometry throughout. No installed font outlines, automatic tracing, or generated raster shapes were imported as font outlines. The new symbols include quadratic segments, converted exactly to cubic curves on import.
- The optional AI exploration used the built-in image-generation tool with the current compiled Party Blob specimen as a style reference. It produced concept boards for `na/in/ec` and `oo/rt`. Ideas informed original vector drawings; no generated pixels were traced or imported. Prompts and images are saved in `concepts/`.
- No distribution license has been selected. Final validation reports only informational `FONT_LICENSE_UNSET`.

## Kerning and creative ligatures

Fourteen original pair exceptions are configured: AV −170, Re −25, Sn −60, up −95, Pa −180, Po −130, Ta −160, To −160, Te −150, Va −110, Wa −90, Ya −150, Fa −100, Fo −80.

The final comparisons in `final-kerning/` show improved rhythm in “Party Blob,” “Tea Today,” “Vase Wave,” and “Yarn Foam Fair.” Pa is already snug; additional tightening would risk contact. `ra` has a tight upper terminal and a large lower cavity, so simply tightening it would not solve the drawing relationship.

The five new ligatures and six added exterior kerning pairs are documented in `ligature-proofs/REVIEW.md`. A separate review font and pre-ligature baseline remain in `ligature-review/`. A treatment that changes perceived letter identity—such as `nn` resembling `m`, removing a distinguishing dot, or extreme kerning that fuses letters—requires user consultation unless full creative freedom was explicitly granted. Optional `dlig` status does not waive that consultation. No such new treatment has been enabled.

## Coordinate and construction record

| Property | Font units / source coordinate |
| --- | --- |
| Units per em | 1000 |
| Ascender | 800 |
| Cap height | 720; SVG y=80 |
| x-height | 420; SVG y=380 |
| Baseline | 0; SVG y=800 |
| Descender | -270; SVG y=1070 |
| Line gap | 30 |
| Shared canvas | 0 0 1000 1070; scale 1 |
| Round overshoot | approximately 10–20 units at cap/x-height/baseline |

This is a heavily modulated design with curved stems, not a uniform-width construction. Approximate horizontal ink sections at font y=200 are retained in `measurements.json`:

- Capital stem family: H left/right 80.1/89.4; I 70.4. Review range 70–90. I is deliberately lighter to avoid a freestanding dark bar.
- Lowercase ascender family: h entry 52.2; l 54.6; t 49.0. Review range 49–56. Descending f is heavier at 71.6.
- Shoulder downstrokes: n 95.5, h 87.3, m 102.8/81.8. Review range 80–105 for tapered shoulders, not straight-stem tolerances.
- Hairline exception: n entry 13.7 at the same section, intentionally extremely thin; m entry 42.5 supports a wider double-shoulder body.
- Round heavy side: o 152.8; g 148.7; p 170.5. The p bowl deliberately carries more mass beside its narrow counter and pendant stem.
- f/t crossbars occupy the same SVG y≈416–459 family. i/j dots reuse the exact same original tilted contour.

The measurements flag families and exceptions; visual acceptance was based on compiled images. Advances and effective sidebearings are stored in the manifest and MCP spacing evidence.

## Repository trial and fixes

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

- Final source revision: `0160db525812d5fa5000d5d51bca1dda700b21b92abddb9691ef1b22939451bf`.
- Backend: FontForge `20251009`.
- Full Python suite: **47 passed**. Ruff passed; Mypy passed for all 13 source files.
- All four edited skills passed `quick_validate.py`.
- Final project validation: no warnings/errors; only the informational license diagnostic.
- Every export: artifact hash and family name verified, 1000 UPM, ascender 800 / descender −270, cap 720 / x-height 420, all 103 encoded characters mapped and shaped without `.notdef` with features off and on.
- `En Engine`: dlig substitutes exactly two `E_n` glyphs in TTF, OTF, and decompressed WOFF2.
- `AV Re Sn up`: kerning preserves glyph names/clusters and reduces advance by exactly 350 units.
- Standard f-sequence sentence: feature comparison has identical shaping because no standard ligatures are configured.
- Compiled visual review: inventory sheet; capital/lowercase rows; digits including I/l/1 and O/0; punctuation in boundaries, time and currency strings; reference words; final kerning OFF/ON sheets at 96 px, scale 3; reference detail at 160 px and a small 32 px raster.
- Browser: the embedded font visibly loads and the updated tester supports capitals, figures, and symbols; feature toggles and unsupported-accent feedback were checked.

`build-report.json` and `acceptance.json` identify the delivered artifacts. Older proof JSONs and transcript entries retain intermediate revisions and failures as evidence; they do not replace the final build report.

## Creative ligatures — delivered

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

## Prototype limits

The reference's expressive rhythm now extends through the flowing ec/in and the nested na/oo/rt. Turning dlig off restores the original independent forms. Hairlines are fragile at 32 px; use larger sizes for this prototype. Further optical polish (especially B/D corners), a broader kerning corpus, accents and language coverage, and production hinting remain future work. The font name and all exported family/PostScript names are Party Blob; historical logs retain an earlier working name.
