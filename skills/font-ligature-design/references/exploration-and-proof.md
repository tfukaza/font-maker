# Original ligature exploration and proof

Read this for candidate exploration, feature isolation, and promotion. Use the original concept and current compiled control, not another reviewer's verdicts.

## Explore with accountable provenance

Record exact case-sensitive input, intended gesture/benefit, proposed feature, test words, and decision. Compare an ordinary sequence, plausible kerning-only alternative, and distinct original replacement ideas at matched scale. Look beyond f combinations when the font suggests shared bowls, shoulders, cut-ins, dots, or swashes. No collision is required, and no ligature count is a goal.

For optional image exploration, follow the available image-generation skill. Supply the actual compiled specimen plus original direction, specify exact text/case, and ask for visibly different constructions on a plain background. Keep the real compiled control beside generated ideas; a regenerated “control” may silently change letters. Inspect spelling, identity, style drift, dots, and counter structure. Label images as concepts, record prompt/provenance, and redraw chosen ideas as original editable SVG paths. Never trace an existing font or treat generated pixels as metric measurements.

Use an isolated study project for speculative active substitutions. Give the study its own project UUID and family/style identity, separate paths and artifacts, and a record of the source revision. Do not overwrite the accepted project's source or exports, and do not promote an identity-changing or materially off-direction design without the approval required by the main skill.

## Build a case-specific matrix

Select actual input strings from configured rules, not just conventional examples. For f combinations, useful starting contexts include `affine profile flower office official difficult affluent offline`, `afig efit aflow rifle fififl`. These do not certify unrelated creative combinations.

For every replacement:

1. Assert the exact input substring is present with the right case. Check that no sheet split severs it or its neighbors.
2. Test an isolated sequence, multiple realistic words, different left/right neighbors, start/end of word, punctuation, and repetitions.
3. Include competing sequences such as `na` and `ap` in `nap`, or short/long f forms. Write the intended winning rule and why before testing, then compare with actual shaping; do not assume chains compose or the longest rule wins. If the preferred reading is undecided, record it as unresolved rather than accepting whichever rule happens to win.
4. Include unrelated negative-control text that should not substitute.
5. Include ordinary and accented neighbors where supported. Inspect dots and any language-dependent distinctions.

Use `shape_text` and `preview_font` from the generated font with explicit settings. A discretionary example:

| Comparison | kern | liga | rlig | dlig |
| --- | --- | --- | --- | --- |
| Ordinary | false | false | false | false |
| Kerning only | true | false | false | false |
| Discretionary ligature | true | false | false | true |
| Replacement, no boundary kerning | false | false | false | true |

Adapt the toggled tag for `liga` or `rlig`, keeping every other setting fixed. An all-off row is diagnostic; it is not a recommendation to disable genuinely required rendering in production.

Verify feature-off component names/clusters and feature-on replacement names, coherent clusters, advances, and offsets. In a kern-only comparison, glyph sequence and clusters must remain unchanged; check the advance delta against actual pair occurrences. Unexpected substitutions or unrelated positioning changes fail even if the image looks plausible.

When a kerning-only alternative requires different pair values, compile it in the isolated study and label it as a separate experimental revision, not merely a feature toggle of the unchanged font. Record each row's source revision, font-byte hash, and scoped source differences; confirm unchanged outlines when claiming a positioning-only comparison. If an old proof cannot be linked to its generating bytes, it may support an observation but cannot certify the current export.

## Inspect design and exported encoding

Inspect word silhouettes, negative space, readable cues, apparent weight, counter openness, entry/exit rhythm, and reference fidelity at reading, native small, and detail sizes. Preserve dots or redesign them consciously; compare `f_i` with `f_l`. A short thin bridge may create a knot without expressing the intended gesture.

Compare ligatures off/on with kerning fixed, then kerning off/on with the replacement held active. Fix internal spacing in its drawing/advance and exterior spacing through justified neighbor relationships. Base-glyph kerning sheets do not clear replacement boundaries.

Inspect each export's Unicode cmap for unintended extra mappings, including presentation forms inferred from production names. Unmapped replacements stay unmapped; manifest declarations alone are not proof. Count only genuine required character mappings for coverage.

Keep SVG and PNG paths, revision, font-byte SHA-256, exact text, complete feature map, size/scale, traces, and observations. Record generated, inspected, accepted, or unresolved status honestly. Explain why the combined drawing is preferable to kerning alone and whether it retains direction. Reject/redraw/omit candidates with no benefit; consultation and unresolved defects block promotion, not further isolated exploration.
