"""Generate two original concept fonts through Font Maker's public MCP tools.

The glyphs are procedural drawings based on two construction systems. No
installed font outlines or raster tracing are used.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

from fontTools.agl import UV2AGL
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).parents[1]
DEFAULT_OUTPUT = ROOT / "archive" / "concept-fonts"
GRID_REFERENCE = Path(
    "/var/folders/61/r756smb95_16p68hfyzwypq40000gn/T/"
    "codex-clipboard-2102ce4d-0490-460d-8814-90a0e6d5bd04.png"
)
FLOW_REFERENCE = Path(
    "/var/folders/61/r756smb95_16p68hfyzwypq40000gn/T/"
    "codex-clipboard-2669787b-5072-46cd-88b7-10486fd9aa22.png"
)


def rows(spec: str, top: int = 0, total: int = 9) -> tuple[str, ...]:
    body = spec.split("/")
    width = len(body[0])
    assert all(len(row) == width for row in body)
    assert top + len(body) <= total
    return tuple(["." * width] * top + body + ["." * width] * (total - top - len(body)))


UPPER = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".####/#..../#..../#..../#..../#..../.####",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".####/#..../#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": ".###./..#../..#../..#../..#../..#../.###.",
    "J": "..###/...#./...#./...#./#..#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#...#/#...#/#...#/#...#",
    "N": "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
}

LOWER: dict[str, tuple[int, str]] = {
    "a": (2, ".###./....#/.####/#...#/.####"),
    "b": (0, "#..../#..../####./#...#/#...#/#...#/####."),
    "c": (2, ".####/#..../#..../#..../.####"),
    "d": (0, "....#/....#/.####/#...#/#...#/#...#/.####"),
    "e": (2, ".###./#...#/#####/#..../.####"),
    "f": (0, ".###./.#.../.#.../####./.#.../.#.../.#..."),
    "g": (2, ".####/#...#/#...#/#...#/.####/....#/.###."),
    "h": (0, "#..../#..../####./#...#/#...#/#...#/#...#"),
    "i": (1, "..#../...../..#../..#../..#../..#.."),
    "j": (1, "...#./...../...#./...#./...#./#..#./.##.."),
    "k": (0, "#..../#..../#...#/#..#./###../#..#./#...#"),
    "l": (0, ".##../..#../..#../..#../..#../..#../.###."),
    "m": (2, ".##.##./#..#..#/#..#..#/#..#..#/#..#..#"),
    "n": (2, "####./#...#/#...#/#...#/#...#"),
    "o": (2, ".###./#...#/#...#/#...#/.###."),
    "p": (2, "####./#...#/#...#/#...#/####./#..../#...."),
    "q": (2, ".####/#...#/#...#/#...#/.####/....#/....#"),
    "r": (2, "#.##./##..#/#..../#..../#...."),
    "s": (2, ".####/#..../.###./....#/####."),
    "t": (0, ".#.../.#.../####./.#.../.#.../.#.../..##."),
    "u": (2, "#...#/#...#/#...#/#...#/.####"),
    "v": (2, "#...#/#...#/#...#/.#.#./..#.."),
    "w": (2, "#...#/#...#/#.#.#/#.#.#/.#.#."),
    "x": (2, "#...#/.#.#./..#../.#.#./#...#"),
    "y": (2, "#...#/#...#/#...#/#...#/.####/....#/.###."),
    "z": (2, "#####/...#./..#../.#.../#####"),
}

DIGITS = {
    "0": ".###./#...#/##..#/#.#.#/#..##/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../.###.",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": "####./....#/....#/.###./....#/....#/####.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../#..../####./....#/....#/####.",
    "6": ".###./#..../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/....#/.###.",
}

SYMBOL_SPECS: dict[str, tuple[int, str]] = {
    "!": (0, "#/#/#/#/#/./#"),
    '"': (0, "#.#/#.#"),
    "#": (1, ".#.#./#####/.#.#./#####/.#.#."),
    "$": (1, ".###./#.#../.###./..#.#/.###."),
    "%": (1, "##..#/##.#./..#../.#.##/#..##"),
    "&": (0, ".##../#..#./.##../#.#../#..#./#..#./.##.#"),
    "'": (0, "#/#"),
    "(": (0, "..#./.#../#.../#.../#.../.#../..#."),
    ")": (0, ".#../..#./...#/...#/...#/..#./.#.."),
    "*": (2, "#.#.#/.###./#####/.###./#.#.#"),
    "+": (2, "..#../..#../#####/..#../..#.."),
    ",": (6, ".#/.#/#."),
    "-": (4, "####"),
    ".": (6, "#"),
    "/": (0, "....#/...#./...#./..#../.#.../.#.../#...."),
    ":": (2, "##/##/../##/##"),
    ";": (2, ".##/.##/.../.##/.##/.#./#.."),
    "<": (1, "...#./..#../.#.../#..../.#.../..#../...#."),
    "=": (2, "#####/...../#####"),
    ">": (1, "#..../.#.../..#../...#./..#../.#.../#...."),
    "?": (0, ".###./#...#/....#/...#./..#../...../..#.."),
    "@": (0, ".####./#....#/#.##.#/#.#..#/#.####/#...../.####."),
    "[": (0, "###/#../#../#../#../#../###"),
    "\\": (0, "#..../.#.../.#.../..#../...#./...#./....#"),
    "]": (0, "###/..#/..#/..#/..#/..#/###"),
    "^": (0, "..#../.#.#./#...#"),
    "_": (8, "#####"),
    "`": (0, "#../.#."),
    "{": (0, "..##/.#../.#../#.../.#../.#../..##"),
    "|": (0, "#/#/#/#/#/#/#"),
    "}": (0, "##../..#./..#./...#/..#./..#./##.."),
    "~": (3, ".##../#..##/....#"),
    "•": (3, "###/###/###"),
    "…": (6, "##.##.##/##.##.##"),
    "\u2013": (4, "######"),
    "—": (4, "########"),
    "\u2018": (0, ".#/#."),
    "\u2019": (0, "#./.#"),
    "“": (0, ".#..#/#..#."),
    "”": (0, "#..#./.#..#"),
}


def all_patterns(style: str | None = None) -> dict[str, tuple[str, ...]]:
    patterns: dict[str, tuple[str, ...]] = {}
    patterns.update({char: rows(spec) for char, spec in UPPER.items()})
    patterns.update({char: rows(spec, top) for char, (top, spec) in LOWER.items()})
    patterns.update({char: rows(spec) for char, spec in DIGITS.items()})
    patterns.update({char: rows(spec, top) for char, (top, spec) in SYMBOL_SPECS.items()})
    patterns[" "] = rows(".....")
    if style == "grid":
        # Super Pixel's lowercase bodies reach 500 units. Keep the dot's
        # 100-unit size/gap by moving it up too, without moving the baseline
        # or j's existing descender. The separate flow study stays unchanged.
        patterns["i"] = rows("..#../...../..#../..#../..#../..#../..#..")
        patterns["j"] = rows("...#./...../...#./...#./...#./...#./#..#./.##..")
    return patterns


def trim_pattern(pattern: tuple[str, ...]) -> tuple[str, ...]:
    occupied = [index for row in pattern for index, value in enumerate(row) if value == "#"]
    if not occupied:
        return pattern
    start, end = min(occupied), max(occupied) + 1
    return tuple(row[start:end] for row in pattern)


def combine(patterns: list[tuple[str, ...]], gap: int = 0) -> tuple[str, ...]:
    trimmed = [trim_pattern(pattern) for pattern in patterns]
    return tuple(("." * gap).join(parts) for parts in zip(*trimmed, strict=True))


def glyph_name(character: str) -> str:
    return UV2AGL.get(ord(character), f"uni{ord(character):04X}")


def points_for(
    pattern: tuple[str, ...], style: str, name: str
) -> dict[tuple[int, int], tuple[float, float]]:
    points: dict[tuple[int, int], tuple[float, float]] = {}
    for row_index, row in enumerate(pattern):
        for column, value in enumerate(row):
            if value != "#":
                continue
            if style == "grid":
                points[(column, row_index)] = (115 + column * 90, 150 + row_index * 100)
                continue
            seed = sum((index + 1) * ord(char) for index, char in enumerate(name))
            jitter_x = ((seed + column * 17 + row_index * 29) % 11) - 5
            jitter_y = ((seed + column * 23 + row_index * 13) % 9) - 4
            lean = (650 - row_index * 100) * 0.055
            points[(column, row_index)] = (
                110 + column * 95 + lean + jitter_x,
                145 + row_index * 95 + jitter_y,
            )
    return points


def polygon_bridge(first: tuple[float, float], second: tuple[float, float], width: float) -> str:
    x1, y1 = first
    x2, y2 = second
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * width / 2, dx / length * width / 2
    # Keep ribbon contours clockwise in the SVG's y-down coordinate system,
    # matching the normalized ellipse contours so nonzero fill cannot cancel
    # where the two overlap after font compilation.
    vertices = [
        (x1 - nx, y1 - ny),
        (x2 - nx, y2 - ny),
        (x2 + nx, y2 + ny),
        (x1 + nx, y1 + ny),
    ]
    return '<polygon points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in vertices) + '"/>'


def _grid_boundary_loops(
    occupied: set[tuple[int, int]],
) -> list[list[tuple[float, float]]]:
    """Trace clockwise outer and counterclockwise inner cell-union boundaries."""

    edges: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    for column, row_index in occupied:
        x0, y0 = 50 + column * 100, 100 + row_index * 100
        x1, y1 = x0 + 100, y0 + 100
        if (column, row_index - 1) not in occupied:
            edges.add(((x0, y0), (x1, y0)))
        if (column + 1, row_index) not in occupied:
            edges.add(((x1, y0), (x1, y1)))
        if (column, row_index + 1) not in occupied:
            edges.add(((x1, y1), (x0, y1)))
        if (column - 1, row_index) not in occupied:
            edges.add(((x0, y1), (x0, y0)))

    direction_index = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    loops: list[list[tuple[float, float]]] = []
    while edges:
        start = min(edges)
        edge = start
        points = [edge[0]]
        while True:
            edges.remove(edge)
            vertex = edge[1]
            if vertex == start[0]:
                break
            points.append(vertex)
            incoming = (
                int(math.copysign(1, vertex[0] - edge[0][0])) if vertex[0] != edge[0][0] else 0,
                int(math.copysign(1, vertex[1] - edge[0][1])) if vertex[1] != edge[0][1] else 0,
            )
            candidates = [candidate for candidate in edges if candidate[0] == vertex]
            if not candidates:
                raise RuntimeError("Open boundary while tracing grid glyph")

            def turn_priority(
                candidate: tuple[tuple[float, float], tuple[float, float]],
                incoming_direction: tuple[int, int] = incoming,
            ) -> int:
                dx = candidate[1][0] - candidate[0][0]
                dy = candidate[1][1] - candidate[0][1]
                outgoing = (
                    int(math.copysign(1, dx)) if dx else 0,
                    int(math.copysign(1, dy)) if dy else 0,
                )
                turn = (direction_index[outgoing] - direction_index[incoming_direction]) % 4
                # At a diagonal contact, trace into the other cell. This makes
                # the two exposed corners concave, so their fillets meet both
                # straight edges tangentially and form a neck without a bulge.
                return {3: 0, 0: 1, 1: 2, 2: 3}[turn]

            edge = min(candidates, key=turn_priority)
        loops.append(points)
    return loops


def _filleted_grid_loop(points: list[tuple[float, float]], radius: float = 25) -> str:
    """Round only concave ink corners, leaving exterior pixel corners square."""

    kappa = 0.5522847498307936
    corners: list[
        tuple[
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
            bool,
        ]
    ] = []
    for index, current in enumerate(points):
        previous = points[index - 1]
        following = points[(index + 1) % len(points)]
        incoming = (
            int(math.copysign(1, current[0] - previous[0])) if current[0] != previous[0] else 0,
            int(math.copysign(1, current[1] - previous[1])) if current[1] != previous[1] else 0,
        )
        outgoing = (
            int(math.copysign(1, following[0] - current[0])) if following[0] != current[0] else 0,
            int(math.copysign(1, following[1] - current[1])) if following[1] != current[1] else 0,
        )
        cross = incoming[0] * outgoing[1] - incoming[1] * outgoing[0]
        rounded = cross < 0
        entry = (
            current[0] - incoming[0] * radius if rounded else current[0],
            current[1] - incoming[1] * radius if rounded else current[1],
        )
        exit_point = (
            current[0] + outgoing[0] * radius if rounded else current[0],
            current[1] + outgoing[1] * radius if rounded else current[1],
        )
        control_in = (
            entry[0] + incoming[0] * radius * kappa,
            entry[1] + incoming[1] * radius * kappa,
        )
        control_out = (
            exit_point[0] - outgoing[0] * radius * kappa,
            exit_point[1] - outgoing[1] * radius * kappa,
        )
        corners.append((entry, exit_point, control_in, control_out, rounded))

    start = corners[0][0]
    commands = [f"M{start[0]:g} {start[1]:g}"]
    for index, (_entry, exit_point, control_in, control_out, rounded) in enumerate(corners):
        if rounded:
            commands.append(
                f"C{control_in[0]:g} {control_in[1]:g} "
                f"{control_out[0]:g} {control_out[1]:g} "
                f"{exit_point[0]:g} {exit_point[1]:g}"
            )
        next_entry = corners[(index + 1) % len(corners)][0]
        if next_entry != exit_point:
            commands.append(f"L{next_entry[0]:g} {next_entry[1]:g}")
    commands.append("Z")
    return "".join(commands)


def grid_art(pattern: tuple[str, ...], name: str) -> tuple[str, int]:
    trimmed = trim_pattern(pattern)
    occupied = {
        (column, row_index)
        for row_index, row in enumerate(trimmed)
        for column, value in enumerate(row)
        if value == "#"
    }
    if not occupied:
        return "", 260

    path_data = "".join(_filleted_grid_loop(loop) for loop in _grid_boundary_loops(occupied))
    width = len(trimmed[0]) if trimmed else 1
    return f'<path d="{path_data}"/>', max(200, width * 100 + 100)


def flow_art(pattern: tuple[str, ...], name: str) -> tuple[str, int]:
    trimmed = trim_pattern(pattern)
    points = points_for(trimmed, "flow", name)
    shapes: list[str] = []
    directions = [(1, 0), (0, 1)]
    for cell, first in sorted(points.items()):
        column, row_index = cell
        for dc, dr in directions:
            neighbor = (column + dc, row_index + dr)
            if neighbor in points:
                shapes.append(polygon_bridge(first, points[neighbor], 160))
        diagonal = (column + 1, row_index + 1)
        if (
            diagonal in points
            and (column + 1, row_index) not in points
            and (column, row_index + 1) not in points
        ):
            shapes.append(polygon_bridge(first, points[diagonal], 150))
        diagonal_up = (column + 1, row_index - 1)
        if (
            diagonal_up in points
            and (column + 1, row_index) not in points
            and (column, row_index - 1) not in points
        ):
            shapes.append(polygon_bridge(first, points[diagonal_up], 150))
    for (column, row_index), (x, y) in sorted(points.items()):
        degree = sum(
            (column + dc, row_index + dr) in points for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
        )
        rx = 82 + (8 if degree <= 1 else 0) + ((column + row_index) % 3 - 1) * 3
        ry = 80 + (6 if degree <= 1 else 0) + ((column * 2 + row_index) % 3 - 1) * 3
        shapes.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx}" ry="{ry}"/>')
    width = len(trimmed[0]) if trimmed else 1
    advance = 250 if not points else max(300, width * 95 + 155)
    return "".join(shapes), advance


def write_svg(path: Path, pattern: tuple[str, ...], style: str, name: str) -> int:
    if style == "grid" and name == "colon":
        pattern = rows("#/././#", top=3)
    elif style == "grid" and name == "semicolon":
        pattern = rows(".#/../../.#/.#/#.", top=3)
    art, advance = grid_art(pattern, name) if style == "grid" else flow_art(pattern, name)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <g id="fontmaker-guides" data-fontmaker-ignore="true">
    <path d="M0 800H1000"/>
  </g>
  <g id="glyph" fill="#000000">{art}</g>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    return advance


async def call(session: ClientSession, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = await session.call_tool(name, arguments)
    if result.is_error:
        raise RuntimeError(f"{name} failed: {result.content}")
    structured = result.structured_content or {}
    if "error" in structured:
        raise RuntimeError(f"{name} failed: {json.dumps(structured['error'], indent=2)}")
    return structured


async def make_font(
    session: ClientSession,
    output_root: Path,
    directory_name: str,
    family_name: str,
    style: str,
    reference: Path,
) -> dict[str, Any]:
    project_path = output_root / directory_name
    if project_path.exists():
        raise RuntimeError(f"Refusing to overwrite existing project: {project_path}")
    created = await call(
        session,
        "create_font_project",
        {
            "path": str(project_path),
            "family_name": family_name,
            "style_name": "Regular",
            "designer": "Font Maker concept study",
            "reference_image": str(reference),
        },
    )
    patterns = all_patterns(style)
    patterns["f_i"] = combine([patterns["f"], patterns["i"]], gap=0)
    patterns["f_l"] = combine([patterns["f"], patterns["l"]], gap=0)

    with tempfile.TemporaryDirectory(prefix=f"fontmaker-{style}-sources-") as temporary:
        source_dir = Path(temporary)
        glyphs: list[dict[str, Any]] = []
        for character, pattern in patterns.items():
            if character in {"f_i", "f_l"}:
                name = character
                codepoints: list[str] = []
            else:
                name = glyph_name(character)
                codepoints = [f"U+{ord(character):04X}"]
            source_id = hashlib.sha256(name.encode("utf-8")).hexdigest()
            source = source_dir / f"{source_id}.svg"
            advance = write_svg(source, pattern, style, name)
            if name == "space" and style == "grid":
                # The rigid, near-monospaced texture needs a more explicit
                # word boundary than the generic quarter-em default.
                advance = 400
            glyphs.append(
                {
                    "name": name,
                    "svg_path": str(source),
                    "codepoints": codepoints,
                    "advance_width": advance,
                }
            )
        imported = await call(
            session,
            "upsert_glyphs",
            {
                "project_id": created["project_id"],
                "expected_revision": created["revision"],
                "glyphs": glyphs,
            },
        )

    if style == "grid":
        kern_pairs = {
            ("A", "V"): -25,
            ("A", "W"): -25,
            ("A", "Y"): -25,
            ("V", "A"): -20,
            ("W", "A"): -20,
            ("Y", "A"): -20,
            ("A", "T"): -20,
            ("T", "A"): -20,
            ("L", "T"): -70,
            ("L", "V"): -50,
            ("L", "Y"): -70,
            ("F", "A"): -20,
            ("P", "A"): -20,
            ("T", "a"): -125,
            ("T", "e"): -125,
            ("T", "o"): -125,
            ("T", "r"): -125,
            ("T", "u"): -125,
            ("T", "y"): -125,
            ("T", "period"): -140,
            ("V", "period"): -140,
            ("Y", "period"): -140,
            ("F", "period"): -180,
            ("r", "period"): -100,
            ("r", "a"): -150,
            ("r", "e"): -25,
            ("r", "o"): -25,
            ("seven", "slash"): -90,
            ("V", "a"): -25,
            ("V", "o"): -20,
            ("Y", "e"): -20,
            ("Y", "o"): -25,
            ("W", "e"): -20,
            ("W", "o"): -20,
        }
    else:
        kern_pairs = {
            (left, right): -45
            for left, right in [
                ("A", "V"),
                ("A", "W"),
                ("A", "Y"),
                ("T", "a"),
                ("T", "o"),
                ("T", "y"),
                ("V", "a"),
                ("Y", "o"),
            ]
        }
    kerned = await call(
        session,
        "set_kerning",
        {
            "project_id": created["project_id"],
            "expected_revision": imported["revision"],
            "upsert_pairs": [
                {"left": left, "right": right, "value": value}
                for (left, right), value in kern_pairs.items()
            ],
        },
    )
    ligatured = await call(
        session,
        "set_ligatures",
        {
            "project_id": created["project_id"],
            "expected_revision": kerned["revision"],
            "upsert": [
                {"feature": "liga", "sequence": ["f", "i"], "replacement": "f_i"},
                {"feature": "liga", "sequence": ["f", "l"], "replacement": "f_l"},
            ],
        },
    )
    proposal = await call(
        session,
        "suggest_spacing",
        {
            "project_id": created["project_id"],
            "glyph_names": ["H", "O", "n", "o"],
            "pair_candidates": [["A", "V"], ["T", "o"]],
        },
    )
    candidate_validation = await call(
        session,
        "validate_font_project",
        {"project_id": created["project_id"], "temporary_build": True},
    )
    previews: list[dict[str, Any]] = []
    preview_cases = [
        ("title", "Snap Engine / Super Rec", True, 76),
        ("uppercase-numbers", "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789", True, 58),
        ("lowercase-ligatures", "abcdefghijklmnopqrstuvwxyz fi fl affine flower!", True, 58),
        ("caps-diagonals", "AVATAR waved to WAYNE by the ivy-covered villa.", True, 48),
        ("round-stems", "Tom took ten tall tools to the old tower.", True, 48),
        (
            "ligatures-on",
            "Five affable office staff efficiently filed flawless affidavits.",
            True,
            46,
        ),
        (
            "ligatures-off",
            "Five affable office staff efficiently filed flawless affidavits.",
            False,
            46,
        ),
        ("punctuation", "“To avoid awkward typography,” Vera said, “fix every pair.”", True, 46),
        ("mixed-case", "Typography Works: Quality, Variety, Rhythm & Style.", True, 46),
        ("numbers", "Invoice 407 totaled $1,729.50 on 11/07/2026.", True, 46),
        (
            "broad-stress",
            "The quick brown fox jumps over a lazy dog; five vivid glyphs follow.",
            True,
            42,
        ),
        (
            "diagnostics",
            "AV VA WA AW AY YA TA AT LT LV LY / To Ta Te Ty Tr Tu Yo Ye Wo We / fi fl ff ffi ffl",
            True,
            40,
        ),
        (
            "control-words",
            "AVATAR WAYWARD WATER Typography / Hamburgefontsiv HAMBURGEFONTSIV",
            True,
            42,
        ),
    ]
    for label, text, ligatures_enabled, font_size in preview_cases:
        preview = await call(
            session,
            "preview_font",
            {
                "project_id": created["project_id"],
                "text": text,
                "features": {"kern": True, "liga": ligatures_enabled},
                "font_size": font_size,
                "guides": False,
            },
        )
        preview["label"] = label
        previews.append(preview)
    candidate_shape = await call(
        session,
        "shape_text",
        {
            "project_id": created["project_id"],
            "text": "AV affine flower",
            "features": {"kern": True, "liga": True},
        },
    )
    ligatures_removed = await call(
        session,
        "set_ligatures",
        {
            "project_id": created["project_id"],
            "expected_revision": ligatured["revision"],
            "upsert": [],
            "remove": [
                {"feature": "liga", "sequence": ["f", "i"]},
                {"feature": "liga", "sequence": ["f", "l"]},
            ],
        },
    )
    candidates_removed = await call(
        session,
        "remove_glyphs",
        {
            "project_id": created["project_id"],
            "expected_revision": ligatures_removed["revision"],
            "names": ["f_i", "f_l"],
        },
    )
    validation = await call(
        session,
        "validate_font_project",
        {"project_id": created["project_id"], "temporary_build": True},
    )
    shaped = await call(
        session,
        "shape_text",
        {
            "project_id": created["project_id"],
            "text": "AV affine flower",
            "features": {"kern": True, "liga": True},
        },
    )
    built = await call(
        session,
        "build_font",
        {"project_id": created["project_id"], "formats": ["ttf", "otf", "woff2"]},
    )
    return {
        "family": family_name,
        "project_path": str(project_path),
        "project_id": created["project_id"],
        "revision": built["revision"],
        "feature_revision": ligatured["revision"],
        "glyph_count": len(patterns) - 2,
        "provenance": (
            "Original project-specific procedural geometry based only on the supplied concept "
            "image; no existing font outlines or raster tracing were used."
        ),
        "spacing_proposal": proposal,
        "candidate_validation": candidate_validation,
        "validation": validation,
        "ligature_review": {
            "decision": "omit",
            "reason": (
                "Compiled on/off word specimens showed no natural fi/fl collision and no "
                "clear visual benefit from substitution."
            ),
            "candidate_revision": ligatured["revision"],
            "final_revision": candidates_removed["revision"],
            "candidate_shape": candidate_shape,
        },
        "shape": shaped,
        "previews": previews,
        "build": built,
    }


async def run(output_root: Path) -> None:
    if not GRID_REFERENCE.is_file() or not FLOW_REFERENCE.is_file():
        raise RuntimeError("The two concept reference images are no longer available")
    output_root.mkdir(parents=True, exist_ok=True)
    parameters = StdioServerParameters(
        command=str(ROOT / ".venv" / "bin" / "fontmaker-mcp"),
        cwd=ROOT,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        reports = [
            await make_font(
                session, output_root, "snap-grid", "Super Pixel", "grid", GRID_REFERENCE
            ),
            await make_font(session, output_root, "snap-flow", "Snap Flow", "flow", FLOW_REFERENCE),
        ]
    (output_root / "build-report.json").write_text(
        json.dumps(reports, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"output": str(output_root), "fonts": [report["family"] for report in reports]},
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    asyncio.run(run(args.output.resolve()))


if __name__ == "__main__":
    main()
