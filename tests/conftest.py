from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def svg_writer():
    def write(path: Path, paths: list[str], *, extra: str = "") -> Path:
        artwork = "".join(f'<path d="{data}"/>' for data in paths)
        path.write_text(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <g id="fontmaker-guides" data-fontmaker-ignore="true">
    <line id="baseline" data-fontmaker-baseline="true" x1="0" x2="1000" y1="800" y2="800"/>
  </g>
  <g id="glyph" fill="#000000">{artwork}{extra}</g>
</svg>
""",
            encoding="utf-8",
        )
        return path

    return write
