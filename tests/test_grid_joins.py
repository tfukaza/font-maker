"""Regression checks for the concept font's diagonal surface-tension joins."""

import runpy
from pathlib import Path
from xml.etree import ElementTree

import pytest
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path

grid_art = runpy.run_path(str(Path(__file__).parents[1] / "examples/generate_concept_fonts.py"))[
    "grid_art"
]


@pytest.mark.parametrize("pattern", [("#.", ".#"), (".#", "#.")])
def test_diagonal_contacts_are_concave_and_tangent(pattern):
    art, _ = grid_art(pattern, "diagonal_fixture")
    root = ElementTree.fromstring(f"<svg>{art}</svg>")
    pen = RecordingPen()
    for path in root:
        assert path.tag == "path"
        parse_path(path.attrib["d"], pen)
    operations = pen.value
    assert sum(op == "moveTo" for op, _ in operations) == 1
    assert sum(op == "closePath" for op, _ in operations) == 1
    assert sum(op == "curveTo" for op, _ in operations) == 2

    for index, (operation, points) in enumerate(operations):
        if operation != "curveTo":
            continue
        start = operations[index - 1][1][-1]
        control1, control2, end = points
        incoming = (control1[0] - start[0], control1[1] - start[1])
        outgoing = (end[0] - control2[0], end[1] - control2[1])
        # With clockwise SVG ink contours, negative turns are concave.
        assert incoming[0] * outgoing[1] - incoming[1] * outgoing[0] < 0
        previous = operations[index - 2][1][-1]
        following = operations[index + 1][1][-1]
        for tangent, edge in [
            (incoming, (start[0] - previous[0], start[1] - previous[1])),
            (outgoing, (following[0] - end[0], following[1] - end[1])),
        ]:
            assert tangent[0] * edge[1] - tangent[1] * edge[0] == pytest.approx(0)
            assert tangent[0] * edge[0] + tangent[1] * edge[1] > 0
