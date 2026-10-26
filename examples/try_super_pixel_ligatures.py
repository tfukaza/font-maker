"""Build isolated, original modular ligature experiments; never edit the base font."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
import sys
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.ttLib import TTFont

from font_maker.models import KerningPair, LigatureRule
from font_maker.preview import compose_preview_svg, shape_font, svg_to_png
from font_maker.service import FontMakerService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from examples.generate_concept_fonts import (
    _filleted_grid_loop,
    _grid_boundary_loops,
    all_patterns,
    trim_pattern,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fonts/super-pixel-fluid"
DEST = ROOT / "archive/super-pixel-ligature-study"
CANDIDATES = {
    "ct": (5, -60, "Factory actor", "Shared upper rail; open c mouth and distinct t stem."),
    "tt": (4, -60, "letter little", "Shared crossbar; two ascenders and separate feet."),
    "st": (5, -60, "system pasta", "S upper terminal continues into t crossbar."),
    "ra": (4, -200, "rare graphic", "Diagonal meniscus between shoulder and nested a cap."),
    "oo": (4, -60, "loop moon", "Shared central stem, two square counters and notched waist."),
}


def draw(sequence: str, offset: int) -> tuple[str, int]:
    cells = set()
    patterns = all_patterns("grid")
    for char, shift in zip(sequence, [0, offset], strict=True):
        pattern = trim_pattern(patterns[char])
        cells.update(
            (x + shift, y)
            for y, row in enumerate(pattern)
            for x, value in enumerate(row)
            if value == "#"
        )
    path = "".join(_filleted_grid_loop(loop) for loop in _grid_boundary_loops(cells))
    # Same canonical canvas and baseline, including for outlines wider than one em.
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">'
        f'<g id="glyph"><path d="{path}"/></g></svg>'
    )
    return svg, (max(x for x, _ in cells) + 1) * 100 + 100


def main() -> None:
    DEST.mkdir()  # Refuse to overwrite an earlier study.
    service = FontMakerService()
    original = service.open_project(str(SOURCE))
    project_path = DEST / "project"
    shutil.copytree(SOURCE, project_path, ignore=shutil.ignore_patterns("build", ".fontmaker"))
    clone_service = FontMakerService()
    opened = clone_service.open_project(str(project_path))
    store, project = clone_service._store_project(opened["project_id"])
    project.project_id = str(uuid.uuid4())
    project.font.family_name = "Super Pixel Ligature Study"
    store.save(project, opened["revision"])
    service = FontMakerService()
    opened = service.open_project(str(project_path))
    pid, revision = opened["project_id"], opened["revision"]
    snapshots = DEST / "snapshots"
    snapshots.mkdir()
    stages = []

    def snapshot(label: str, dlig: bool) -> None:
        build = service.build(pid, ["ttf"])
        target = snapshots / (label + ".ttf")
        shutil.copy2(project_path / build["artifacts"][0]["path"], target)
        stages.append((label, target, dlig, build["revision"]))

    snapshot("ordinary", False)
    revision = service.set_kerning(
        pid,
        revision,
        upsert_pairs=[
            KerningPair(left=seq[0], right=seq[1], value=data[1])
            for seq, data in CANDIDATES.items()
        ],
    ).revision
    snapshot("kerning-only", False)
    # Restore base pair spacing before adding optional replacement glyphs.
    original_service = FontMakerService()
    original_service.open_project(str(SOURCE))
    _, base = original_service._store_project(original["project_id"])
    store, project = service._store_project(pid)
    project.kerning = base.kerning.model_copy(deep=True)
    revision = store.save(project, revision)
    drawings = DEST / "drawings"
    drawings.mkdir()
    inputs = []
    for sequence, (offset, _, _, _) in CANDIDATES.items():
        svg, advance = draw(sequence, offset)
        path = drawings / (sequence + ".svg")
        path.write_text(svg)
        inputs.append(
            dict(name="_".join(sequence), svg_path=str(path), codepoints=[], advance_width=advance)
        )
    revision = service.upsert_glyphs(pid, revision, inputs).revision
    revision = service.set_ligatures(
        pid,
        revision,
        upsert=[
            LigatureRule(feature="dlig", sequence=list(seq), replacement="_".join(seq))
            for seq in CANDIDATES
        ],
    ).revision
    snapshot("ligature", True)
    _, project = service._store_project(pid)
    proofs = DEST / "proofs"
    proofs.mkdir()
    records = []
    for sequence, (_, _, words, _idea) in CANDIDATES.items():
        for size, scale in [(64, 3), (24, 1)]:
            pieces, y, width = [], 12, 0
            for label, font, dlig, stage_revision in stages:
                text = sequence + " / " + words
                shaping = shape_font(font, text, {"kern": True, "liga": False, "dlig": dlig})
                if dlig:
                    assert "_".join(sequence) in [g["glyph_name"] for g in shaping["glyphs"]]
                svg = ET.fromstring(
                    compose_preview_svg(font, project, shaping, font_size=size, guides=False)
                )
                svg.set("x", "0")
                svg.set("y", str(y + 18))
                pieces.append(
                    f'<text x="24" y="{y + 10}" font-size="10" '
                    f'font-family="sans-serif">{html.escape(label)}</text>'
                )
                pieces.append(ET.tostring(svg, encoding="unicode"))
                width = max(width, int(svg.attrib["width"]))
                y += int(svg.attrib["height"]) + 30
                records.append(
                    dict(
                        sequence=sequence,
                        text=text,
                        stage=label,
                        size=size,
                        scale=scale,
                        revision=stage_revision,
                        shaping=shaping,
                    )
                )
            data = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}">'
                '<rect width="100%" height="100%" fill="white"/>' + "".join(pieces) + "</svg>"
            ).encode()
            stem = proofs / f"{sequence}-{size}"
            stem.with_suffix(".svg").write_bytes(data)
            stem.with_suffix(".png").write_bytes(svg_to_png(data, pixel_scale=scale))
        # Review replacement boundaries separately from internal drawing.
        for kern in [False, True]:
            records.append(
                dict(
                    sequence=sequence,
                    stage="boundary",
                    kern=kern,
                    shaping=service.shape(
                        pid,
                        "a" + sequence + "o " + sequence * 2 + ".",
                        {"kern": kern, "liga": False, "dlig": True},
                    ),
                )
            )
    for sequence in CANDIDATES:
        off = service.shape(pid, sequence, {"kern": True, "liga": False, "dlig": False})
        on = service.shape(pid, sequence, {"kern": True, "liga": False, "dlig": True})
        assert [g["glyph_name"] for g in off["glyphs"]] == list(sequence)
        assert [g["glyph_name"] for g in on["glyphs"]] == ["_".join(sequence)]
        assert on["glyphs"][0]["cluster"] == 0
    for text in ["fi fl", "ctt", "ttt", "oooo", "scat"]:
        records.append(
            dict(
                stage="overlap-negative",
                text=text,
                shaping=service.shape(pid, text, {"dlig": True, "liga": False, "kern": True}),
            )
        )
    diagnostics = [d.model_dump(mode="json") for d in service.validate(pid, temporary_build=True)]
    assert not any(d["severity"] == "error" for d in diagnostics)
    build = service.build(pid, ["ttf", "otf", "woff2"])
    for artifact in build["artifacts"]:
        with TTFont(project_path / artifact["path"]) as font:
            assert len(font.getBestCmap()) == 103
    assert original_service.open_project(str(SOURCE))["revision"] == original["revision"]
    report = dict(
        source=original,
        revision=revision,
        candidates={s: d[3] for s, d in CANDIDATES.items()},
        diagnostics=diagnostics,
        build=build,
        records=records,
        snapshots={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshots.iterdir()},
        status="Exploratory only; no changes to released Super Pixel.",
    )
    (DEST / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    from examples.render_ligature_study import render

    render(DEST)
    print(DEST)


if __name__ == "__main__":
    main()
