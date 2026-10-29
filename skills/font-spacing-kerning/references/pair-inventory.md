# Plan kerning coverage from the glyphs

Use this guide to turn a font's actual spacing risks into reproducible pair coverage. It is a discovery aid, not an exhaustive universal list of troublesome letters or prescribed adjustments.

## Inventory the relevant sides

Inspect canonical SVG contours and compiled glyphs with kerning disabled. For each candidate, record its character or glyph ID, relevant left/right side, feature, and likely gap or collision pattern. Include zero-kerning glyphs: existing kerning tables only show earlier decisions, not all possible problems.

Common Latin starting points include:

| Feature to inspect | Example characters | What changes the neighboring white space |
| --- | --- | --- |
| Diagonals and wedges | `A V W X Y K R Z v w x y k z` | Sloping sides, low/high triangular cavities, projecting vertices, diagonal serifs |
| Upper overhangs or open lower sides | `T F P L 7 f r t` | Crossbars, shoulders, beaks, feet, or hooks that constrain one height while leaving another open |
| Round or open sides | `B C D G O Q S b c d e g o p q s 0 3 6 8 9` | Bowl curvature, aperture direction, overshoot, stress, and tails; left/right sides need separate judgments |
| Narrow or asymmetric forms | `I J i j l a` | Narrow bodies, dots, descenders, shoulders, or unequal side cavities |
| Marks and attachments | `.,:;!? ' " ‘ ’ “ ” - – — ( ) [ ] { } / \\` | Attachment distance, tall/low clearances, and the different behavior of opening versus closing marks |
| Font-specific extensions | Accented letters, `&`, `@`, currency signs, alternate glyphs, ligatures | Accent overhang, unusual terminals, widened joins, tails, or substituted-glyph boundaries |

These are not kerning classes. A serif `W` and a sans-serif `W`, or `O` and `Q` in the same font, can require different inventories. Add any other glyph whose drawn shape creates a risk, including ordinary straight-sided forms with unusual serifs or width. Remove an example from the risk inventory only with a design-specific reason; it may still be an essential neighbor or control. Scripts beyond Latin require their own glyph inventory and shaping contexts.

## Expand to ordered combinations

Let `E` be all supported neighboring characters in the declared review scope and `C` the inventoried candidates. For a full pass, generate:

`(C × E) ∪ (E × C)`

Use every ordered pair in that union; include `cc` for each candidate and deduplicate identical codepoint sequences. Do not lowercase, remove uncommon letter combinations, or restrict neighbors to vowels or candidates alone. Uppercase–uppercase, lowercase–lowercase, uppercase–lowercase, and lowercase–uppercase combinations all belong when those characters are supported. Include figures, punctuation, and symbols; review spaces separately as word boundaries. For explicit exhaustive character-pair coverage, use `E × E`.

Exclude unsupported or out-of-scope scripts/features explicitly. If a pair is shaped through a substitution, record the actual glyph sequence and feature settings; review substituted-glyph boundary kerning with that replacement enabled. A character-pair matrix does not by itself cover every unencoded alternate or ligature boundary; replacements have their own edges and need the dedicated pass in [Re-space ligature replacements](../SKILL.md#re-space-ligature-replacements).

Use the [proof script's character-set options](proof-script.md) for ordered products and reverse pairs. Split large matrices into bounded sheets, retaining their inventory and review ledger. The product size is planned workload, not completed review.

For a targeted report such as a wide `We`, start with that exact case-sensitive sequence. Inspect the relevant `W` side against the font's other round/open forms, related capitals and lowercase diagonals where their geometry supports comparison, and words that exercise any changed rule. Broaden when that evidence exposes a recurring pattern. Label remaining matrix entries unreviewed; a targeted correction does not certify the whole font.

## Review, track, and revisit

Compare kerning OFF/ON in paired proofs and exact-sequence words at display and reading sizes. Judge the shape and distribution of white space across heights, nearest approaches, and adjacent control gaps; neither equal bounding-box distance nor absence of collision establishes optical balance. Geometry measurements may rank candidates, but cannot accept them visually.

Track each exact pair with its risk reason, proof location, font revision/hash, features, sizes, and outcome. Keep these distinctions visible:

- **Planned/unreviewed:** selected for coverage, no inspected proof yet.
- **Generated:** a proof exists; no visual judgment has been made.
- **Inspected:** the actual image was opened and an observation recorded.
- **Accepted:** a reason supports the current zero or nonzero adjustment, including context checks.
- **Unresolved:** an issue, uncertainty, missing glyph, or unverified change remains, with a next action.

Report unique planned pairs, generated pairs, visually inspected pairs, accepted pairs, unresolved pairs, and exclusions. Do not infer acceptance from generated images, a default status, class membership, or a successful build. It is valid to accept zero kerning. It is not valid to assign one nonzero value across a Cartesian product without visual evidence.

Group rules only after confirming equivalent relevant sides, inspect members and exceptions, and retain the exact-pair coverage record. When a new contour risk appears in words, expand the inventory and matrix. Outline or bearing changes invalidate affected pair conclusions; regenerate and inspect those proofs before closing them.
