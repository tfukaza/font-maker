# Hakiland Display Regular — display prototype 0.114

Open `specimen.html` in a browser to type with the font. Install either
`build/fonts/HakilandDisplay-Regular.ttf` or `.otf`; `.woff2` is the webfont.

This revised prototype contains 103 encoded characters: A–Z, a–z, 0–9, printable ASCII,
curly quotes, en/em dashes, bullet, and ellipsis. No accented letters,
combining-mark positioning, additional weights, or ligatures are included.
Designed primarily for headings at 32 px and above.

The supplied artwork guided original vector construction; no existing font
outlines were imported or traced. The design uses high contrast, wedge serifs,
diamond dots, parallel stem/crossbar families and shared diagonal angles.
User refinements: single triangular g ear; a faceted Q tail with parallel edges;
reference-led a/d bowls and a slanted d foot. Curves retain optical compensation. The latest Q/a/d are revised candidates, not user-approved drawings.

`font.yaml` and `glyphs/` are the editable Font Maker sources. `refined/` contains individually edited source SVGs; the generator gives these priority and never overwrites them. `drawings/` has
readable codepoint filenames. The reproducible drawing script is
`source/build_wedge.py` (run within the Font Maker repository/environment).
`quality-report.json` records format coverage, measured bounds, metrics,
shaping and hashes. `specimen.svg` is a vector proof; `specimen.png` is its render.

Font license: not assigned. Font Maker's own software license does not assign
a license to this font. All possible kerning combinations have not been
individually reviewed.

Latest refinements: compact a lower bowl, larger i/j dots, compensated diagonal weights, optically reviewed spacing, and the perceived-weight and design-consistency passes recorded in `weight-review.json` and `consistency-review.json`, including the tapered 7. `spacing-refinement.json` is loaded on each rebuild.
