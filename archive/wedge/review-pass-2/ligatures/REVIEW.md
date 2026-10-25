# Hakiland Display v0.111 — ligature review

Recommendation: retain separate glyphs and no active ligature substitutions. Add **+24 units to fb, fh, fk, fl** to prevent the f terminal and following upper-left serif from reading as an accidental join. This is a modest local clearance adjustment, not a general increase in f spacing.

Reviewed the original concept, actual SVG outlines, and compiled forms at 64 px (3× proofs), 180 px (4× detail), and native 24 px. The source is revision `4b03087526b719ffe2972ed1b48e64a3a23e2a470b7d9aaf23d1e8c421772cb3`, TTF SHA-256 `777dde9cdbf31f71213188fdf42f90c200122e62e180a1e2e456329302f64704`.

## Why these four pairs need spacing

The f top wedge and the b/h/k/l crown approach to approximately **14.10 units** at their nearest contours. They remain separate but look nearly tangent, particularly at 24 px. The isolated +24-unit trial increases that minimum to approximately **34.44 units** while keeping word rhythm. Measurements use 64 subdivisions per compiled quadratic curve; they support the image judgment rather than prescribe a clearance target.

The ordinary, kern-off, and current-kern forms are identical for f pairs, because this version contains no f kern entries. The trial differs only in the four stated kerning rules and its study family/project identity. Every compiled glyph outline and hmtx metric was compared with the source and is identical. The master was not modified.

Inspect `spacing-trial-1.png` for the four pairs; `spacing-trial-2.png` for **flower flow offline affluent**; `spacing-trial-3.png` for **offkey offbeat offhand**; and the `spacing-trial-native-*` images for actual 24 px rendering. `spacing-terminal-detail.png` isolates the crown gap. The +24 correction is visually preferable to making this contact into a new join: the two triangular terminals keep their individual purpose and the f arch remains faithful to the reference.

## Candidate inventory and decisions

| Exact inputs | Geometry or opportunity inspected | Decision |
| --- | --- | --- |
| fi, fj | f overhang beside diamond dot and slanted stem head | Dots remain separate, prominent, and readable. The closest clearances are about 65.80 and 74.47 units. No collision requires a replacement; omit liga and preserve dots. |
| fl, fk, fb, fh | f wedge beside matching upper-left crown | Kerning-only +24 gives a cleaner gap without changing either letter. No replacement needed. |
| ff, ffi, ffl | Repeated curved caps and aligned crossbars | Separate caps and crossbars have an even rhythm. A shared rail would add a join without a demonstrated need. ffl receives exactly one +24 adjustment at its trailing fl; ffi stays unchanged. |
| ft | Aligned crossbars, unlike upper terminals | Crossbars remain separate and t stays distinct. No functional collision or proven expressive benefit. |
| Qu, Qa, Qo, Qy | Under-bowl Q ribbon could suggest a continuing swash | Ribbon and next letter are already clear. Extending it would compete with the geometric, restrained direction and add a third gesture. Preserve separate forms. |
| ra, ri, ro, rr | r diamond beside bowls, dots, and repeated terminals | Distinct diamonds remain recognizable; existing kerning gives room. A bridge would suppress open negative space; no replacement justified. |
| tt, st, ct | Repeated or complementary crossbars/terminals | Words letter, pasta, actor remain clear. Shared crossbars or cap arcs would introduce connected lettering not evidenced by the concept. No default or discretionary join recommended. |
| nn, nm, mm | Shared shoulders and vertical stem rhythm | Minimum/manner retain readable repeated stems. Sharing a stem would risk nn reading as m. No identity-changing study was drawn or enabled. |
| AV, VA, AW, WA | Parallel diagonals and wedge terminals | Kerning already improves the spaces while separate forms preserve the design. Joining would add unnecessary dark junctions. |

## Behavior checks

- All proof rows retain full feature maps, revision, font-byte hash, text, size/scale and HarfBuzz traces in `records.json`.
- `liga`, `rlig`, and `dlig` toggles produce no replacement or unrelated change in either source or trial; both retain exactly 103 mapped characters.
- Trial glyph names and clusters match source sequences. Total advance increases by exactly 24 times the occurrence count of fb/fh/fk/fl, including repeated sequences and punctuation boundaries.
- Explicit ff, ffi, ffl, ffli, flfl, fflffi, offhand, and unrelated-word checks distinguish overlapping f sequences. No chaining is assumed because no substitution is configured.
- Proposed rules and source/trial provenance are in `report.json` and `trial.json`. `trial-project/` has a unique project UUID and study name, and is not a production export.

All generated proof images in this folder were visually inspected. This is a scoped ligature-need review, not a claim to exhaust all possible decorative combinations. No ligature artwork was drawn because the inspected candidates showed no advantage over the separate forms plus the four local spacing adjustments. No dot removal or identity-changing replacement was enabled.
