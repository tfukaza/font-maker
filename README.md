# Font Maker

Font Maker is a stateful local MCP font workshop for agents. It turns project-aligned SVG glyphs into a durable font project with explicit metrics, reviewable spacing proposals, kerning, ligatures, compiled previews, validation, and TTF/OTF/WOFF2 exports.

Font Maker accepts artwork; it does not trace concept images automatically. Give an image-capable agent a concept image and the generated `glyph-template.svg`, then use the MCP tools to import and refine its SVGs.

## Install for development

Python 3.12 and [`uv`](https://docs.astral.sh/uv/) are required. The native FontForge compiler is isolated in a short-lived process and never loaded into the MCP server.

On macOS:

```bash
brew bundle
uv sync --all-extras --python 3.12
fontmaker doctor
```

Font Maker 0.1.0 requires FontForge internal version `20251009`. On Linux, install a matching build, run `uv sync --all-extras --python 3.12`, and verify it with `fontmaker doctor`. A custom executable can be selected with `FONTMAKER_FONTFORGE`. We do not silently fall back to an unpinned system version.

The repo-local [`.mcp.json`](.mcp.json) launches `uv run --project . fontmaker-mcp`. The plugin manifest is [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json).

## Workflow

1. Call `create_font_project` with a family name and optional reference image. It creates a schema-versioned `font.yaml` and a shared-coordinate SVG template with one canonical baseline.
2. Draw each glyph inside the template's `#glyph` group and call `upsert_glyphs`. Imports are path-confined, strictly validated, safely normalized, and transactional as a batch.
3. Inspect and set metrics. `suggest_spacing` returns a revision-bound proposal; it never edits the project until `apply_spacing_proposal` is called.
4. Configure kerning groups/pairs and `liga`, `rlig`, or `dlig` ligatures.
5. Call `validate_font_project`, `shape_text`, and `preview_font` before `build_font`.

Every durable mutation requires the revision returned by the previous inspection or mutation. The manifest and canonical SVGs are the source of truth; SQLite and build artifacts are disposable.

## Companion CLI

The CLI uses the same service layer as MCP:

```bash
fontmaker doctor
fontmaker --version
fontmaker init ./paper-sans --family "Paper Sans"
fontmaker check ./paper-sans
fontmaker shape ./paper-sans --text "AV affine"
fontmaker preview ./paper-sans --text "AVATAR affine" --scale 3 --out preview.png
fontmaker build ./paper-sans --format ttf --format otf --format woff2
```

## Project contents

- [`docs/architecture.md`](docs/architecture.md) describes the product and project format.
- [`templates/glyph-template.svg`](templates/glyph-template.svg) is the default 1000 UPM template; each project receives a metric-specific generated copy.
- [`skills/`](skills/) contains an end-to-end production workflow plus focused guidance for metrics and SVG construction, spacing and kerning, ligatures, outline QA, and specimen review.
- [`tests/`](tests/) includes a real FontForge/HarfBuzz acceptance fixture for `AV` kerning and an `fi` ligature.

## FontForge acknowledgement

Font Maker is built around [FontForge](https://fontforge.org/), the free and open-source font editor created by George Williams and maintained by the FontForge contributors. FontForge is the compilation backend and is available as a complete program under the GNU General Public License, version 3 or any later version. Font Maker itself is distributed under the same `GPL-3.0-or-later` license.

Font Maker is not affiliated with or endorsed by the FontForge project. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for source and license information.
