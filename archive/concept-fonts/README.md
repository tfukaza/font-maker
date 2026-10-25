# Concept font dogfood build

These two fonts were drawn from scratch from the supplied concept images with Font Maker. No existing font outlines or glyph sets were used.

## Super Pixel

- 103 encoded glyphs: uppercase and lowercase Latin, figures, printable ASCII punctuation, and selected typographic symbols.
- Square modular construction with concave meniscus fillets at inside contacts and restrained surface-tension necks at diagonal contacts.
- Tightened optical base spacing, a 400-unit word space, a narrow `i`, and visually reviewed kerning including `Ty`, `ra`, `LT/LY/LV`, period attachment, and `7/`.
- Colon and semicolon dots use the same 100-unit module as the period; the semicolon tail matches the comma.
- No ligatures in the final build: the visual feature-on/off review did not justify them for this geometric design.

The Super Pixel project has moved to the `fonts/super-pixel/` directory (its review notes are in `fonts/super-pixel/REVIEW.md`). Installable files are named `SuperPixel-Regular.ttf`, `.otf`, and `.woff2`, and their internal font family is **Super Pixel**.

Generate reusable kerning review sheets with:

```shell
.venv/bin/python skills/font-spacing-kerning/scripts/render_kerning_proofs.py fonts/super-pixel --pair ra --text "rare Typography parallel; 12:30"
```

Each run creates PNG/SVG comparisons and an `index.json` with exact shaping evidence and pending visual-review entries. Default examples are not exhaustive.

## Snap Flow

- 103 encoded glyphs in a soft, high-contrast, ribbon-like display style.
- No ligatures in the final build after visual comparison; the unligated sequences remain legible and better preserve the concept's rhythm.

Each project contains its authoritative `font.yaml`, normalized per-glyph SVGs, TTF/OTF/WOFF2 files, SVG previews, and high-resolution PNG previews. The tool is GPL-3.0-or-later and uses FontForge; the licensing metadata for these generated fonts is intentionally unset until the designer chooses it.

Regenerate everything with:

```shell
.venv/bin/python examples/generate_concept_fonts.py
```
