---
name: font-ligature-design
description: Explore and draw original functional or expressive ligatures, choose features, verify substitutions and boundaries, and protect readability and design intent. Use for collision repair or creative joining language; use spacing and kerning for positioning-only changes.
---

# Font Ligature Design

Explore a font's expressive vocabulary as well as awkward sequences. A shared curve, counter, terminal, swash, or coordinated cut-in may add value without any collision. Draw from scratch, reusing only this project's own original components; never derive replacements from existing fonts.

Judge compiled words visually. Numeric clearance and advance totals establish behavior, not beauty. Keep the original concept or approved design direction beside proofs: a technically clean join that changes rounded forms into sharp hooks may be stylistic drift, not an improvement.

## Discover candidates from this design

For expressive display work, inspect recurring gestures and intended words rather than stopping at `fi/fl`. Consider shared shoulders, complementary bowls, crossbars, interacting dots, and repeated-letter rhythms. Derive candidates from the actual shapes; no universal inventory is required.

Compare **ordinary**, **kerning-only**, and **original replacement** constructions at matched apparent scale. Explain the intended benefit in word silhouette, negative space, rhythm, personality, and readable letter cues. A thin bridge or simply tighter placement is not evidence of a resolved drawing. Explore distinct constructions when the idea is unresolved, using the [exploration and proof procedure](references/exploration-and-proof.md).

Conventional `fi fl ff ffi ffl` are useful candidates where the `f` overhang affects dots or ascenders, not mandatory deliverables. A geometric or naturally open face may need none. Other combinations are not “standard” merely because they can join. Keep a ligature only for a demonstrated functional or intentional visual benefit; omission is a valid outcome.

## Respect identity and approval boundaries

Unless full creative freedom was explicitly granted for the relevant treatment, consult before enabling a construction that changes perceived letters: `nn` resembling `m`, a distinguishing dot disappearing, or an extreme kern visually fusing another character. Optional `dlig` does not waive consultation.

Prepare the exact sequence, ordinary and proposed word-level renderings, intended feature/default behavior, and readability tradeoff. Keep unapproved artwork or an isolated study font separate from accepted active features. Generic permission to explore, use image generation, or enable a different ligature is not blanket approval. Record approval and scope; do not repeatedly ask about an already authorized treatment.

Routine recognizable joins within approved direction can proceed. Explicit freedom still requires readability checks and disclosure of intentional ambiguity. If a candidate departs materially from the concept's terminal, curvature, or weight language, show that departure and seek direction before promoting it as the new style.

## Choose feature behavior

- `liga`: standard, normally enabled but user-disableable ligatures.
- `dlig`: optional ornamental, historical, or logo-like combinations.
- `rlig`: required for correct rendering, not a way to force a decorative preference.

Font Maker v1 uses the default Latin language system without per-language exceptions. Preserve language-required dots and distinctions, or omit inappropriate default substitutions. It does not author ligature caret positions; report that limitation when editing/selection behavior matters.

## Draw and implement original replacements

Use stable names preserving component identity and case, such as `f_i` or `E_n`. Normally leave replacements **unmapped**; OpenType operates on the original character stream and does not need Unicode presentation-form mappings. Inspect exported cmap entries too: a glyph name may invite backend inference, so manifest intent alone is insufficient.

Preserve component scale, baseline, stroke families, ascenders, and counter openness. Carry curve tension and thick/thin transitions through shared gestures without dark knots. For f combinations, decide dot treatment deliberately, keep `f_l` distinct from `f_i`, and resolve both terminals in longer forms rather than stacking pair patches.

Give the replacement a deliberate advance; summing components is only a comparison point. Match entry/exit rhythm, but do not assume base kerning-group membership automatically applies to replacements. Redrawing changes the entry and exit edges, so every replacement—and every later redraw of one—needs its own sidebearing and boundary-kerning pass under [spacing and kerning](../font-spacing-kerning/SKILL.md), including removal of copied pairs the new edges no longer justify. Symbol-like replacements usually want more room than letters. Reuse original project geometry only, flattened and validated under [outline QA](../font-outline-qa/SKILL.md).

Import replacement glyphs before `set_ligatures`, always using the latest revision. Fix absent components or replacements first; reopen conflicts rather than replaying stale mutations. For longer forms, define the intended direct sequence and verify actual shaping, not assumed chaining.

## Prove the actual behavior and design

Follow the [proof procedure](references/exploration-and-proof.md) with `shape_text` and `preview_font`. Use explicit maps for `kern/liga/rlig/dlig`; hold other features fixed when toggling one. Check glyph names, clusters, advances, offsets, and unrelated text. Exercise overlapping substitutions and both exterior boundaries, including repeated sequences and punctuation.

Verify each test word contains the exact case-sensitive input and that shaping actually reaches the intended replacement. Generic f sentences do not clear unrelated creative combinations. Compare feature-on/off with kerning fixed, then kerning off/on with the replacement enabled. Internal spacing belongs to drawing and advance; boundary kerning belongs to neighboring glyphs. Confirm the replacement's outer gaps are even on both sides and match the intended relationship to its components, and that no inherited pair survives whose contour reason the new drawing removed.

Keep SVGs and use PNG `pixel_scale=3` for words, `4` for join details, plus separate `1` at actual small text size. Record size, scale, revision, **font-byte SHA-256**, features, and trace. Split long proofs without cutting target sequences or their neighbors.

Actually inspect clean words beside the concept and ordinary control. Explain whether the join improves rhythm while retaining readable cues and design direction. Reject, redraw, or omit closed counters, dark joints, lost dots, unapproved identity changes, or treatments needing pervasive boundary exceptions. Record generated, inspected, accepted, and unresolved states separately; an isolated attractive pair is not final acceptance.
