# Third-party notices

## FontForge

Font Maker is designed to invoke FontForge as its font compilation backend.

- Project: FontForge
- Original creator: George Williams
- Maintainers and copyright holders: the FontForge contributors
- Homepage: https://fontforge.org/
- Source used by Font Maker 0.1.0: https://github.com/fontforge/fontforge/tree/20251009
- License information: https://github.com/fontforge/fontforge/blob/master/LICENSE
- Complete-program license: GNU General Public License, version 3 or any later version (`GPL-3.0-or-later`)

FontForge's license file explains that the complete program is available under GPL-3.0-or-later and that many individual parts are available under the revised BSD license. Any Font Maker distribution that includes a FontForge binary, modified FontForge code, or a container containing FontForge must also carry the notices and corresponding source/license materials required for that exact distribution.

Font Maker is not affiliated with or endorsed by the FontForge project.

This notice records attribution and project provenance. It is not a substitute for the full license text or corresponding-source obligations when GPL-covered software is distributed.

## Other runtime components

Font Maker also uses the following separately licensed open-source projects through locked Python dependencies:

- Model Context Protocol Python SDK (`mcp`), MIT License, https://github.com/modelcontextprotocol/python-sdk
- fontTools, MIT License, https://github.com/fonttools/fonttools
- uharfbuzz and HarfBuzz, Apache-2.0 and HarfBuzz's project license respectively, https://github.com/harfbuzz/uharfbuzz and https://github.com/harfbuzz/harfbuzz
- resvg-py and resvg, MIT and MPL-2.0 respectively, https://pypi.org/project/resvg/ and https://github.com/linebender/resvg
- Pydantic, MIT License, https://github.com/pydantic/pydantic
- ruamel.yaml, MIT License, https://pypi.org/project/ruamel.yaml/

The authoritative versions and transitive dependency set are recorded in `uv.lock`. Their licenses remain their respective authors' licenses; inclusion here does not relicense them.
