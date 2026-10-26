# Super Pixel coding and ASCII ligatures

Super Pixel Fluid and Super Pixel Bitmap **1.001** include 21 standard coding
ligatures and 11 discretionary expressions. [View both families](ligature-preview.png).
The original 103 encoded characters, outlines, advances, project identities, and
kerning pairs remain intact. Both fonts remain proportional.

## Using the fonts

Use the rebuilt TTF, OTF, WOFF, or WOFF2 files under each family's `build/fonts/`
directory. Coding ligatures use `liga`, normally enabled by a shaping application.
Expressions use `dlig`, disabled by default. If an editor disables ligatures,
enable its font-ligature setting; application support varies.

```css
/* Coding operators, without expressive substitutions. */
.code { font-feature-settings: "liga" 1, "dlig" 0; }
/* Coding operators plus sideways faces and hearts. */
.expressions { font-feature-settings: "liga" 1, "dlig" 1; }
/* Original separate characters. */
.plain { font-feature-settings: "liga" 0, "dlig" 0; }
```

The underlying text remains ASCII. Each replacement retains the sum of its
component advances, with existing exterior kerning inherited where applicable.
There are no new Unicode mappings. These fonts do not provide explicit ligature
caret positions; cursor placement and selection within a ligature depend on the
application.

## Inventory and visual review — 2026-10-25

All sequences below were inspected individually in compiled proofs for both
families and accepted. Designs use the existing 100-unit grid, square exposed
corners, Fluid's concave fillets, and Bitmap's square contours. No external font
artwork was used. The original project ampersands supply the two `&&` components.

| Feature | Sequences | Accepted treatment |
| --- | --- | --- |
| `liga` | `->`, `<-`, `<->` | Continuous single shaft and open stepped arrowheads. |
| `liga` | `=>`, `<=>` | Two parallel shafts, preserving the equal-sign distinction. |
| `liga` | `\|>`, `<\|` | Separate pipe and shorter open chevron, with no filled triangle. |
| `liga` | `==`, `===` | Continuous two-bar and three-bar forms, respectively. |
| `liga` | `!=`, `!==` | Diagonal cancellation across two or three bars; diagonal ends remain visible. |
| `liga` | `<=`, `>=` | Compact relational chevron above a separated equality bar. |
| `liga` | `&&` | Two identifiable ampersands with a rising shared terminal. |
| `liga` | `\|\|` | Two distinct parallel bars aligned to the operator body. |
| `liga` | `??`, `?.` | Aligned question stems and dots; both question marks or the property dot remain distinct. |
| `liga` | `::`, `:=` | Dots aligned with the operator rows; open gaps retained. |
| `liga` | `..` | Two centered range dots, clearly separate from baseline ellipsis. |
| `liga` | `...` | Conservative baseline ellipsis, retaining the original dot rhythm. |
| `dlig` | `:)`, `:-)` | Sideways eyes and a stepped curved smile; optional nose retained. |
| `dlig` | `:(`, `:-(` | Reversed curved mouth, retaining the frown direction. |
| `dlig` | `;)`, `;-)` | Descending wink mark and curved smile, with or without a nose. |
| `dlig` | `:D`, `:-D` | Open, compact D-shaped mouth with a visible counter. |
| `dlig` | `:P`, `:-P` | P-shaped mouth with distinct bowl and descending tongue/stem. |
| `dlig` | `<3` | Pixel heart with two lobes and a centered descending point. |

Initial smile sketches resembled chevrons; the accepted mouths use a three-cell
vertical run to retain their curved facial reading. Negative-space channels in
the arrows and comparisons remain open at the inspected sizes. The widest bars
deliberately occupy the original character span instead of shortening code lines.

Longer sequences take precedence over shorter prefixes: `!==`, `===`, `<=>`,
and `...` are direct replacements. Thus `====` shapes as `===` followed by `=`,
and `....` as `...` followed by `.`. When both features are enabled, coding rules
run before expressions: `(::)` retains the `::` operator instead of ending in a
smiley. Substitutions are literal font rules, not a programming-language parser.

## Evidence and reproduction

- [Fluid review and proofs](super-pixel-fluid/LIGATURES.md)
- [Bitmap review and proofs](super-pixel-bitmap/LIGATURES.md)
- [Combined SVG overview](ligature-preview.svg)

Each family's `build/previews/coding-ligatures/` contains off/on SVG and PNG sheets
at 20, 24, and 30px with native raster scale, plus 60px sheets at 3× scale. Separate
30px code/expression contexts exercise boundaries. The reports record font-byte
SHA-256, project revision, exact text, features, sizes, scales, and shaping traces.
Generated reports do not themselves declare visual acceptance; this review does.

All 64 replacement sources were checked for closed contours. Fluid's actual
Bézier handles were checked for tangent entry and exit; Bitmap has only grid-aligned
line segments. Both families have identical occupied cells per sequence. All
32 designs in both families were visually inspected in the 30px overview and
24px off/on sheets; Bitmap's complete 20px sheets were also inspected. The
100px, 4× `join-details` strips were inspected for arrow channels, strict-inequality
joins, ampersand connections, curved smile mouths, and the heart notch in both
styles. Code, expression, and inherited-kerning context strips were inspected too.

```sh
.venv/bin/python examples/add_super_pixel_ligatures.py
.venv/bin/pytest -q
```

The updater preserves project identity and original glyph records. A repeat run
produced byte-identical manifests without duplicate glyphs, rules, or kerning pairs.
The complete suite passed **81 tests**, including all eight font exports, feature
isolation, widths, clusters, overlapping sequences, boundary kerning, unchanged
text, cmap checks, shared cells, and a fresh FontForge build. Focused Ruff checks
also passed.
