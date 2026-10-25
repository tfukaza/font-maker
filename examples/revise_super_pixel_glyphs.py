"""Redraw Super Pixel's l, c and C from the generator's grid patterns and rebuild."""

from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

from font_maker.service import FontMakerService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from examples.generate_concept_fonts import all_patterns, write_svg

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "fonts" / "super-pixel"
GLYPHS = ["l", "c", "C"]


def main() -> None:
    service = FontMakerService()
    opened = service.open_project(str(PROJECT))
    pid, revision = opened["project_id"], opened["revision"]
    _, project = service._store_project(pid)
    assert not any(
        {pair.left, pair.right} & set(GLYPHS) for pair in project.kerning.pairs
    ), "kerning would need review"
    patterns = all_patterns("grid")
    with tempfile.TemporaryDirectory(prefix="super-pixel-revise-") as temporary:
        inputs = []
        for name in GLYPHS:
            record = project.glyphs[name]
            # Hash the name: "c.svg" and "C.svg" collide on case-insensitive disks.
            source = Path(temporary) / f"{hashlib.sha256(name.encode()).hexdigest()}.svg"
            advance = write_svg(source, patterns[name], "grid", name)
            assert advance == record.advance_width, (name, advance, record.advance_width)
            inputs.append(
                dict(
                    name=name,
                    svg_path=str(source),
                    codepoints=record.codepoints,
                    advance_width=record.advance_width,
                    left_side_bearing=record.left_side_bearing,
                    right_side_bearing=record.right_side_bearing,
                )
            )
        revision = service.upsert_glyphs(pid, revision, inputs).revision

    diagnostics = service.validate(pid, temporary_build=True)
    assert not any(d.severity == "error" for d in diagnostics), diagnostics
    service.build(pid, ["ttf", "otf", "woff2"])
    fonts = PROJECT / "build" / "fonts"
    with TTFont(fonts / "SuperPixel-Regular.ttf") as font:
        assert len(font.getBestCmap()) == 103
        font.flavor = "woff"
        font.save(fonts / "SuperPixel-Regular.woff")
    _, png = service.preview(
        pid, "Illinois 1l Il| cC Cocoa clock", font_size=72, pixel_scale=2, guides=False
    )
    previews = PROJECT / "build" / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    (previews / "l-c-revision-2026-10-25.png").write_bytes(png)
    print(revision)


if __name__ == "__main__":
    main()
