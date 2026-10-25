# Super Pixel ligature study

Source Super Pixel revision: `e50989f66f119603b8c51d6840e816bcc4710deb9b14e68eaeda95543a3074f7`.
Study revision: `d5d1cdffea718bb708770cadfc6c52e466a7fbda7d30f7a48964b7afe094f1cc`.

The released font is unchanged. All five drawings are original constructions from the project's own modular geometry. They are optional `dlig` substitutions in a separately named study font, not approved additions to the release. Their glyphs remain unmapped; all 103 original encoded characters are preserved.

## Visual decisions

| Sequence | Decision | Evidence |
| --- | --- | --- |
| tt | Strongest candidate | Shared crossbar gives a deliberate repeated-stem rhythm. Two ascenders and separate feet retain both letters. `letter` and `little` remain clear at native 24px. |
| st | Promising optional display join | Upper rail flows into t; stepped s middle and t ascender remain recognizable in `system` and `pasta`. Weight is coherent, without a swollen junction. |
| ct | Keep for user comparison | `Factory` and `actor` are readable, but connecting the top makes the c slightly d-like at small size. The ordinary/kerning-only versions are calmer. |
| ra | Reject this construction | The shoulder closes the upper opening in a, creating stacked counters and an 8-like form. The resulting cluster is busy and more identity-changing than the ordinary pair. |
| oo | Emblem experiment only | Open square counters and a clean shared stem, but the spectacles-like unit compresses the normal letter rhythm. Needs explicit approval of that visual treatment before promotion. |

The main agent and an independent reviewer inspected all ten three-way comparison PNGs at 64 units/3× and native 24px/1×. Each compares ordinary spacing, a plausible tighter kerning-only value, and the joined drawing. Main-agent follow-up also inspected repeated replacements and a/o/period boundaries, plus 180-unit/4× closeups of tt, ra, and oo. The joins have tangent concave fillets, not circular overlays. This is a focused experiment, not exhaustive font acceptance.

## Try and inspect

- Open [specimen.html](specimen.html) locally and turn on “Experimental ligatures (dlig)”. The toggle enables all five experiments; the fixed comparison rows show ordinary and experimental text side by side.
- [tt comparison](proofs/tt-64.png), [st comparison](proofs/st-64.png), [ct comparison](proofs/ct-64.png), [ra comparison](proofs/ra-64.png), [oo comparison](proofs/oo-64.png).
- SVG companions remain available beside each PNG; native small proofs end in `-24.png`, join details in `-detail.png`, and boundary samples in `-boundary.png`.
- [Build and shaping evidence](report.json) records revisions, hashes, formats, clusters, advances, and feature settings.

The browser tool blocked local file navigation, so the specimen's interactive browser check is pending. The compiled PNGs were inspected directly. The page embeds the exact study WOFF2, records its hash, flags unsupported characters, and hides the font previews on loading failure.

## Technical verification

TTF, OTF, and WOFF2 builds pass validation with only the informational unset-font-license diagnostic. Each candidate shapes to exactly one intended replacement under `dlig`, retains its two original glyphs when disabled, and reports cluster zero in the isolated pair. Overlap checks yielded `ctt → c_t t`, `ttt → t_t t`, and `oooo → o_o o_o`; `fi fl` and `scat` remain unchanged. Boundary shaping was recorded with kerning both on and off.

This experiment uncovered FontForge inferring U+FB06 from the unmapped name `s_t`. The compiler now explicitly assigns the manifest's Unicode mapping and clears inferred aliases. A regression test verifies the unmapped replacement and functional GSUB in all three formats. The full suite passed: 47 tests.

The first-pass output, including its unintended presentation-form mapping, is retained separately in `../super-pixel-ligature-study-initial` for diagnostic provenance; use only this final study for comparison or download.

Regeneration: `examples/try_super_pixel_ligatures.py` creates a fresh study and refuses to overwrite an existing one. `examples/render_ligature_study.py` can refresh the specimen from an existing study report and font artifacts. No source font files are modified.
