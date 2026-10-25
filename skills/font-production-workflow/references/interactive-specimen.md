# Interactive specimen handoff

Use this checklist when delivering or refreshing a prototype/release. Reuse the project's existing `specimen.html`; it is a derived proof, not an outline source.

## Package the exact reviewed font

- Make the page local and self-contained with embedded project WOFF2, or bundle relative font files. No remote fonts or network dependencies.
- Show family/style, source revision, SHA-256 of the actual font bytes, chosen coverage profile, and prototype limitations. Link matching exports.
- After rebuilding, refresh embedded bytes or revisioned URLs and metadata together. A cached previous font is not evidence for a new revision.
- Keep letter spacing neutral by default; cosmetic tracking must not hide kerning problems.

## Make behavior truthful

Provide editable sample text, a size range from small to display, and independent kerning and configured ligature toggles. Name the actual `liga`, `rlig`, or `dlig` feature. Show when no ligatures exist instead of implying they are mandatory.

Derive supported codepoints from the compiled cmap, not a hard-coded alphabet. Flag unsupported typed characters and show exact missing characters/codepoints. Browser fallback must not masquerade as coverage. A cmap entry is necessary but still needs visual verification of the drawing.

Wait for the intended font to load and expose a visible loading failure instead of silently presenting fallback. Include targeted sample strings from the [corpus](../../font-specimen-review/references/test-corpus.md), plus sequences drawn from active rules. Show the original concept or a link to it when useful for comparing direction.

## Verify in a browser

Open the local page through an allowed browser surface. Confirm intended font loading, then test custom text, size changes, independent feature toggles, unsupported input, and downloads. Compare representative words at small and display sizes with the static proofs. Confirm downloaded bytes match the displayed revision/hash.

If browser access is unavailable or blocked, do not circumvent the restriction or infer success from HTML source. Mark browser verification pending and describe which static checks did run. Record the revision checked; a later rebuild requires fresh verification.

Link the page and exports at handoff, alongside unresolved coverage/design issues. An interactive page complements actual shaped PNG/SVG proofs and their feature traces; it cannot replace them.
