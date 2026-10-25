# Targeted specimen corpus

Use these as **non-exhaustive starting samples**, then derive cases from actual shapes, configured rules, requested languages, and observed defects. Pangrams provide breadth; targeted strings find failures faster. Verify exact case-sensitive substrings and actual shaping before claiming a pair or replacement was tested.

## Sentences

- Caps and diagonals: `AVATAR waved to WAYNE by the ivy-covered villa.`
- Round-to-stem: `Tom took ten tall tools to the old tower.`
- F ligatures: `Five affable office staff efficiently filed flawless affidavits.`
- Quotes and punctuation: `“To avoid awkward typography,” Vera said, “fix every pair.”`
- Mixed case: `Typography Works: Quality, Variety, Rhythm & Style.`
- Numbers: `Invoice 407 totaled $1,729.50 on 11/07/2026.`
- Broad stress: `The quick brown fox jumps over a lazy dog; five vivid glyphs follow.`

For supported text, compare the f-ligature sentence with the relevant feature enabled and disabled, kerning held fixed. It exposes replacements and underlying spacing, but does not certify unrelated display ligatures. Missing characters remain missing coverage, not passes.

## Compact diagnostics

```text
HHHH HHOH HOOH OOOO
nnnn nnonn noon oooo
HHIHH HOHOO nninn nonoo
nxin nixn minimum
njn ijij
HIOX HOHO
hbdkl hnh bnb dnd knk lnl
pqgjy npn nqn ngn njn nyn
0123456789 0000 1111 8888
AV VA WA AW AY YA TA AT LT LV LY
To Ta Te Ty Tr Tu Yo Ye Wo We
Va Vo Ya Yo ra re ro ry rv ar
fi fl ff ffi ffl
AVATAR WAYWARD WATER Typography
Hamburgefontsiv HAMBURGEFONTSIV
rare rara parallel retro robot
Il1 O0 rn m cl d b p q
12:30 a;b. $1,234.50 50% a@b.com (a+b)/2
```

Check whether `Ty`, `ra`, `re`, and `ro` appear where claimed: `Typography`, `rare`, `retro`, and `robot` are suitable; `more` contains `or`, not `ro`. Pair lists are examples, never an exhaustive whitelist.

Review word boundaries in sentences, not just isolated pairs. Compare colon/semicolon weight against period/comma and the `i` dot; punctuation prominence can be wrong without a collision.

Use `nxin nixn minimum` to compare Latin body tops, and `njn ijij` for dot clearance and descending forms. Start with explicit `kern=false, liga=false, rlig=false, dlig=false` diagnostic settings so substitutions do not hide base-letter height differences; this is a diagnostic view, not a production feature recommendation. Inspect `i`/`j` stems and dots separately against the project's x-height, with guide-overlaid and clean companions. Add `ı í ï` only when mapped, and report missing coverage rather than accepting fallback. Height consistency is a construction check, not proof of visual quality.

Use the cap/round, ascender, descender, and figure rows to exercise the [full metrics audit](../../font-design-metrics/SKILL.md), not merely x-height. Compare the declared families and optical zones, not one universal height or width. Add repeated components and supported accented forms from the actual design. Review multiple stacked lines as well as single lines for accent/descender clearance and clipping; if a preview tool only renders one line, use the local specimen or another permitted renderer and record that evidence separately.

## Coverage and accents

Generate rows from the chosen machine-readable inventory and actual cmap; do not use a pangram as a coverage test. Include uppercase, lowercase, digits, symbols, quotes/dashes, currencies, and every required accent. For supported characters, compare:

```text
Í Ó ÍÓ í ó íó
À Á Ä Å È É Ë Ì Í Ï Ò Ó Ö Ù Ú Ü
à á ä å è é ë ì í ï ò ó ö ù ú ü
Çç Ññ Šš Ÿÿ ı
$10 €10 £10 ¥10 10¢
```

These accent samples are not a language inventory. Add required missing families from the project brief and inspect stacked lines for clipping and mark clearance. Check narrow/wide capitals/lowercase, optical centering, dot handling, baseline-below marks, and neighbor spacing. Mark unsupported cases precisely rather than rendering fallback.

For each active ligature derive separate exact-sequence words, boundary cases, repetitions, and overlapping-rule tests using the [ligature proof procedure](../../font-ligature-design/references/exploration-and-proof.md).
