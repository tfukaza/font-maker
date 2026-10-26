# Super Pixel Bitmap 1.001 — ligature review

Added 21 default `liga` coding operators and 11 optional `dlig` expressions.
All 32 replacement designs are accepted following the
[shared inventory and review](../LIGATURES.md). Every new source uses square,
grid-aligned contours and the same occupied cells as Fluid. Sideways faces retain
curved step patterns without introducing Bézier curves.

- [Combined family preview](../ligature-preview.png)
- [Arrows, off/on at 20px](build/previews/coding-ligatures/page-1-20.png)
- [Comparisons and logic, off/on at 20px](build/previews/coding-ligatures/page-2-20.png)
- [Punctuation and faces, off/on at 20px](build/previews/coding-ligatures/page-3-20.png)
- [Expressions, off/on at 20px](build/previews/coding-ligatures/page-4-20.png)
- [Generating revision, font hash, and traces](build/previews/coding-ligatures/report.json)

Reviewed TTF SHA-256:
`e658e237c00b9b031abf93ab1c2b75d506d26b58713483f252dfeac471676316`.
TTF, OTF, WOFF, and WOFF2 exports have matching sequence coverage and unchanged
103-codepoint mappings. Original glyph sources and metrics were preserved.
