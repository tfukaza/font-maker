"""Update both existing Super Pixel projects and produce reproducible ligature proofs.

Run from the repository root: .venv/bin/python examples/add_super_pixel_ligatures.py
Only this script's unmapped glyphs, rules, and inherited boundary pairs are upserted.
"""

from __future__ import annotations

import hashlib
import html
import json
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.ttLib import TTFont

from font_maker.models import KerningPair, LigatureRule
from font_maker.preview import compose_preview_svg, shape_font, svg_to_png
from font_maker.service import FontMakerService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from examples.generate_concept_fonts import _filleted_grid_loop, _grid_boundary_loops
from examples.make_super_pixel_bitmap import occupied_cells, outline, square_loop

ROOT = Path(__file__).resolve().parents[1]
CODING = (
    "->", "<-", "<->", "=>", "<=>", "|>", "<|",
    "==", "===", "!=", "!==", "<=", ">=", "&&", "||", "??", "?.",
    "::", ":=", "..", "...",
)
EXPRESSIONS = (":)", ":-)", ":(", ":-(", ";)", ";-)", ":D", ":-D", ":P", ":-P", "<3")
SEQUENCES = CODING + EXPRESSIONS
FEATURES_OFF = {"kern": True, "liga": False, "rlig": False, "dlig": False}


def glyph_name(sequence: str) -> str:
    # ASCII hex avoids special characters, case collisions, and cmap inference.
    return "code_" + "_".join(f"{ord(char):02x}" for char in sequence)


def pattern_cells(rows: tuple[str, ...], x: int = 0, y: int = 0) -> set[tuple[int, int]]:
    return {(x + col, y + row) for row, line in enumerate(rows)
            for col, value in enumerate(line) if value == "#"}


def draw_cells(sequence: str, advance: int, bases: dict[str, set[tuple[int, int]]]) -> set[tuple[int, int]]:
    """Original per-operator cell constructions on the font's existing lattice."""
    width = advance // 100 - 1
    cells: set[tuple[int, int]] = set()

    def rail(y: int, start: int = 0, end: int | None = None) -> None:
        cells.update((x, y) for x in range(start, width if end is None else end))

    def head(right: bool, tip: int, center: int = 3, radius: int = 3) -> None:
        cells.update((tip + (-abs(dy) if right else abs(dy)), center + dy)
                     for dy in range(-radius, radius + 1))

    if sequence in {"->", "<-", "<->", "=>", "<=>"}:
        left, right = sequence.startswith("<"), sequence.endswith(">")
        if left:
            head(False, 0)
        if right:
            head(True, width - 1)
        if "=" in sequence:
            for y in (2, 4):
                rail(y, 1 if left else 0, width - (1 if right else 0))
        else:
            rail(3)
    elif sequence in {"|>", "<|"}:
        # Retain both the pipe and open chevron; no filled play-button triangle.
        pipe = 0 if sequence == "|>" else width - 1
        cells.update((pipe, y) for y in range(7))
        head(sequence == "|>", width - 1 if sequence == "|>" else 0, radius=2)
    elif sequence in {"==", "===", "!=", "!=="}:
        for y in ((1, 3, 5) if sequence in {"===", "!=="} else (2, 4)):
            rail(y)
        if sequence.startswith("!"):
            # The diagonal spans all bars and projects beyond them at both ends.
            center = width // 2
            cells.update((center + 3 - y, y) for y in range(7))
    elif sequence in {"<=", ">="}:
        # A 5px chevron centered on the equals bars, one cell before them.
        head(sequence == ">=", 1 if sequence == "<=" else 3, center=4, radius=2)
        for y in (3, 5):
            rail(y, 5)
    elif sequence == "||":
        cells = {(x, y) for x in (0, 2) for y in range(1, 6)}
    elif sequence == "&&":
        # Two recognizable ampersands, connected by a rising shared terminal.
        cells = bases["&"] | {(x + 6, y) for x, y in bases["&"]}
        cells.update({(5, 5), (6, 4)})
    elif sequence in {"??", "?."}:
        # A more compact question hook with aligned lower stem and dot.
        question = pattern_cells((".###.", "#...#", "....#", "...#.", "...#.", ".....", "...#."))
        cells = question
        if sequence == "??":
            cells |= {(x + 6, y) for x, y in question}
        else:
            cells.add((6, 6))
    elif sequence == "::":
        cells = {(x, y) for x in (0, 2) for y in (2, 4)}
    elif sequence == ":=":
        cells = {(0, 2), (0, 4)}
        rail(2, 2)
        rail(4, 2)
    elif sequence in {"..", "..."}:
        # Range dots sit at the operator center; ellipsis retains baseline dots.
        cells = {(2 * index, 3 if sequence == ".." else 6) for index in range(len(sequence))}
    elif sequence == "<3":
        cells = pattern_cells((".##...##.", "####.####", "#########", ".#######.",
                               "..#####..", "...###...", "....#...."), (width - 9) // 2)
    else:
        # Sideways eyes, optional nose, and a deliberately drawn mouth.
        cells = {(0, 2), (0, 4)}
        if sequence.startswith(";"):
            cells.add((1, 5))
        mouth = sequence[-1]
        if mouth in "()":
            # A three-cell vertical run makes a curved mouth, not an arrowhead.
            rows = ("#.", ".#", ".#", ".#", "#.") if mouth == ")" else (".#", "#.", "#.", "#.", ".#")
            cells |= pattern_cells(rows, width - 2, 1)
        elif mouth == "D":
            cells |= pattern_cells(("###.", "#..#", "#..#", "#..#", "###."), width - 4, 1)
        else:
            cells |= pattern_cells(("###.", "#..#", "###.", "#...", "#..."), width - 4, 1)
        if "-" in sequence:
            mouth_start = width - (2 if mouth in ")(" else 4)
            rail(3, 3, mouth_start - 1)
    assert cells and all(0 <= x < width and 0 <= y <= 7 for x, y in cells), sequence
    return cells


def source_svg(cells: set[tuple[int, int]], bitmap: bool) -> str:
    draw_loop = square_loop if bitmap else _filleted_grid_loop
    data = "".join(draw_loop(loop) for loop in _grid_boundary_loops(cells))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">'
            f'<g id="glyph" fill="#000000"><path d="{data}"/></g></svg>')


def update_project(root: Path, definitions: dict[str, tuple[set[tuple[int, int]], int]],
                   char_names: dict[str, str]) -> tuple[FontMakerService, str]:
    service = FontMakerService()
    opened = service.open_project(str(root))
    pid, revision = opened["project_id"], opened["revision"]
    store, project = service._store_project(pid)
    base_records = {name: record.model_dump() for name, record in project.glyphs.items()
                    if not name.startswith("code_")}
    base_hashes = {name: hashlib.sha256((root / record["source"]).read_bytes()).hexdigest()
                   for name, record in base_records.items()}
    with tempfile.TemporaryDirectory(prefix="super-pixel-ligatures-") as temporary:
        inputs = []
        for sequence, (cells, advance) in definitions.items():
            name = glyph_name(sequence)
            path = Path(temporary) / f"{name}.svg"
            path.write_text(source_svg(cells, "bitmap" in root.name))
            inputs.append(dict(name=name, codepoints=[], svg_path=str(path), advance_width=advance))
        revision = service.upsert_glyphs(pid, revision, inputs).revision
    revision = service.set_ligatures(pid, revision, upsert=[
        LigatureRule(feature="liga" if sequence in CODING else "dlig",
                     sequence=[char_names[char] for char in sequence], replacement=glyph_name(sequence))
        for sequence in sorted(SEQUENCES, key=lambda value: (-len(value), value))
    ]).revision
    # Preserve existing exterior kerning, including T.. and :PA.
    _, project = service._store_project(pid)
    pairs = [pair for pair in project.kerning.pairs
             if not pair.left.startswith("code_") and not pair.right.startswith("code_")]
    boundaries = {glyph_name(seq): (char_names[seq[0]], char_names[seq[-1]]) for seq in SEQUENCES}
    inherited = []
    for pair in pairs:
        lefts = [pair.left] + [name for name, (_, last) in boundaries.items() if last == pair.left]
        rights = [pair.right] + [name for name, (first, _) in boundaries.items() if first == pair.right]
        inherited.extend(KerningPair(left=left, right=right, value=pair.value)
                         for left in lefts for right in rights if (left, right) != (pair.left, pair.right))
    revision = service.set_kerning(pid, revision, upsert_pairs=inherited).revision
    store, project = service._store_project(pid)
    project.font.version = "1.001"
    store.save(project, revision)
    # The YAML emitter leaves a space before wrapping long source paths. Keep
    # newly added entries whitespace-clean without reformatting existing glyphs.
    manifest = store.manifest_path.read_text()
    for sequence in SEQUENCES:
        prefix = f"  {glyph_name(sequence)}:\n    source:"
        manifest = manifest.replace(prefix + " \n", prefix + "\n")
    store.manifest_path.write_text(manifest)
    assert base_records == {name: project.glyphs[name].model_dump() for name in base_records}
    assert all(hashlib.sha256((root / project.glyphs[name].source).read_bytes()).hexdigest() == digest
               for name, digest in base_hashes.items())
    diagnostics = service.validate(pid, temporary_build=True)
    assert not any(item.severity == "error" for item in diagnostics), diagnostics
    service.build(pid, ["ttf", "otf", "woff2"])
    basename = project.font.postscript_name
    with TTFont(root / "build/fonts" / f"{basename}.ttf") as font:
        font.flavor = "woff"
        font.save(root / "build/fonts" / f"{basename}.woff")
    return service, pid


def make_proofs(root: Path, service: FontMakerService, pid: str) -> None:
    store, project = service._store_project(pid)
    font = root / "build/fonts" / f"{project.font.postscript_name}.ttf"
    destination = root / "build/previews/coding-ligatures"
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    groups = [SEQUENCES[index:index + 8] for index in range(0, len(SEQUENCES), 8)]
    for page, sequences in enumerate(groups, 1):
        for size, scale in [(20, 1), (24, 1), (30, 1), (60, 3)]:
            pieces, y, width = [], 30, 0
            for sequence in sequences:
                label = html.escape(sequence)
                pieces.append(f'<text x="12" y="{y}" font-family="monospace" font-size="12">{label} — off / on</text>')
                y += 8
                for enabled in (False, True):
                    features = {**FEATURES_OFF, "liga": enabled, "dlig": enabled}
                    text = f"a{sequence}b  ({sequence})"
                    shaped = shape_font(font, text, features)
                    svg = ET.fromstring(compose_preview_svg(font, project, shaped, font_size=size, guides=False))
                    svg.set("x", "0")
                    svg.set("y", str(y))
                    pieces.append(ET.tostring(svg, encoding="unicode"))
                    width = max(width, int(svg.attrib["width"]))
                    y += int(svg.attrib["height"])
                    records.append(dict(sequence=sequence, font_size=size, pixel_scale=scale, shaping=shaped))
                y += 20
            data = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}">'
                    '<rect width="100%" height="100%" fill="white"/>' + "".join(pieces) + '</svg>').encode()
            stem = destination / f"page-{page}-{size}"
            stem.with_suffix(".svg").write_bytes(data)
            stem.with_suffix(".png").write_bytes(svg_to_png(data, pixel_scale=scale))
    contexts = ["value !== null && count >= 0", "(x) => x?.name ?? fallback", "left <-> right -> next",
                "a === b || a != c", "Type::member := source |> next", "0..10 ... done",
                "Hello :) ;-) :D :P <3", "T.. V... F... r.. :PA :-PA"]
    for enabled in (False, True):
        for index, text in enumerate(contexts):
            features = {**FEATURES_OFF, "liga": enabled, "dlig": enabled}
            shaped = shape_font(font, text, features)
            svg = compose_preview_svg(font, project, shaped, font_size=30, guides=False)
            stem = destination / f"context-{index}-{'on' if enabled else 'off'}"
            stem.with_suffix(".svg").write_bytes(svg)
            stem.with_suffix(".png").write_bytes(svg_to_png(svg, pixel_scale=1))
            records.append(dict(font_size=30, pixel_scale=1, shaping=shaped))
    shaped = shape_font(font, "<=> !== && :) <3", {**FEATURES_OFF, "liga": True, "dlig": True})
    svg = compose_preview_svg(font, project, shaped, font_size=100, guides=False)
    (destination / "join-details.svg").write_bytes(svg)
    (destination / "join-details.png").write_bytes(svg_to_png(svg, pixel_scale=4))
    records.append(dict(font_size=100, pixel_scale=4, shaping=shaped))
    report = dict(revision=store.revision(project), font_sha256=hashlib.sha256(font.read_bytes()).hexdigest(),
                  status="generated; visual inspection recorded separately in LIGATURES.md", records=records)
    (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n")


def make_overview() -> None:
    pieces = ['<rect width="100%" height="100%" fill="white"/>',
              '<text x="20" y="25" font-family="sans-serif" font-size="16">Super Pixel ligatures — Fluid above, Bitmap below; liga + dlig enabled</text>']
    for family_index, family in enumerate(("fluid", "bitmap")):
        service = FontMakerService()
        root = ROOT / f"fonts/super-pixel-{family}"
        opened = service.open_project(str(root))
        _, project = service._store_project(opened["project_id"])
        font = root / "build/fonts" / f"{project.font.postscript_name}.ttf"
        for index, sequence in enumerate(SEQUENCES):
            x, y = (index % 4) * 250, (index // 4) * 145 + 45
            if family_index == 0:
                pieces.append(f'<text x="{x + 16}" y="{y + 12}" font-family="monospace" font-size="14">{html.escape(sequence)}</text>')
            shaped = shape_font(font, f"a{sequence}b", {**FEATURES_OFF, "liga": True, "dlig": True})
            svg = ET.fromstring(compose_preview_svg(font, project, shaped, font_size=30, guides=False))
            svg.set("x", str(x))
            svg.set("y", str(y + 17 + family_index * 50))
            pieces.append(ET.tostring(svg, encoding="unicode"))
    data = ('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1210">'
            + "".join(pieces) + '</svg>').encode()
    (ROOT / "fonts/ligature-preview.svg").write_bytes(data)
    (ROOT / "fonts/ligature-preview.png").write_bytes(svg_to_png(data, pixel_scale=1))


def main() -> None:
    source = ROOT / "fonts/super-pixel-fluid"
    service = FontMakerService()
    opened = service.open_project(str(source))
    _, project = service._store_project(opened["project_id"])
    char_names = {chr(int(cp[2:], 16)): name for name, glyph in project.glyphs.items() for cp in glyph.codepoints}
    widths = {char: project.glyphs[name].advance_width for char, name in char_names.items()}
    bases = {char: occupied_cells(outline(source / project.glyphs[name].source)) for char, name in char_names.items()}
    definitions = {}
    for sequence in SEQUENCES:
        advance = sum(widths[char] for char in sequence)
        definitions[sequence] = draw_cells(sequence, advance, bases), advance
    for family in ("fluid", "bitmap"):
        root = ROOT / f"fonts/super-pixel-{family}"
        service, pid = update_project(root, definitions, char_names)
        make_proofs(root, service, pid)
        print(f"Updated {root.name}: {len(CODING)} coding + {len(EXPRESSIONS)} expression ligatures", flush=True)
    make_overview()


if __name__ == "__main__":
    main()
