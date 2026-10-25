"""Draw original 5x9 bitmap glyphs with tiny diagonal-contact fillets.

Run with Python 3. The SVG uses no installed fonts or external resources.
"""

from pathlib import Path
import json
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
CELL = 24
RADIUS = 0.28  # In logical pixels. Zero restores the exact square bitmap.
COLS, ROWS = 72, 28

# Each glyph has exactly five columns and nine rows. Capitals occupy rows
# 0..6; lowercase bodies rows 2..6; descenders rows 7..8.
def glyph(rows, top):
    result = ["....."] * top + rows
    result += ["....."] * (9 - len(result))
    assert len(result) == 9 and all(len(row) == 5 for row in result)
    return result


GLYPHS = {
    "S": glyph([".####", "#....", "#....", ".###.", "....#", "....#", "####."], 0),
    "E": glyph(["#####", "#....", "#....", "####.", "#....", "#....", "#####"], 0),
    "R": glyph(["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"], 0),
    "n": glyph(["####.", "#...#", "#...#", "#...#", "#...#"], 2),
    "a": glyph([".###.", "....#", ".####", "#...#", ".####"], 2),
    "p": glyph(["####.", "#...#", "#...#", "#...#", "####.", "#....", "#...."], 2),
    "g": glyph([".####", "#...#", "#...#", "#...#", ".####", "....#", ".###."], 2),
    "i": glyph(["..#..", ".....", "..#..", "..#..", "..#..", "..#.."], 1),
    "e": glyph([".###.", "#...#", "#####", "#....", ".####"], 2),
    "u": glyph(["#...#", "#...#", "#...#", "#...#", ".####"], 2),
    "r": glyph([".###.", "#....", "#....", "#....", "#...."], 2),
    "c": glyph([".####", "#....", "#....", "#....", ".####"], 2),
}

# Fractional changes at exposed ends, separate from the original bitmap.
# The replacement rectangle is (x, y, width, height) in logical pixels.
# These cells do not participate in diagonal contacts, so the existing
# surface-tension bridges can continue to use the original pixel masks.
RECT_OVERRIDES = {
    "E": {(3, 3): (3, 3, 0.75, 1)},       # Shorter middle arm.
    "e": {(4, 6): (4, 6, 0.75, 1)},       # Open the lower terminal slightly.
    "g": {(1, 8): (0.75, 8, 1.25, 1)},    # Extend the tail to the left.
    "r": {(3, 2): (3, 2, 1.375, 1)},      # Lengthen the shoulder to the right.
}


def contacts(pixels):
    """Yield only vertices with two diagonally opposed occupied quadrants."""
    for y in range(1, 9):
        for x in range(1, 5):
            nw, ne = (x - 1, y - 1) in pixels, (x, y - 1) in pixels
            sw, se = (x - 1, y) in pixels, (x, y) in pixels
            if nw and se and not ne and not sw:
                yield x, y, [(1, -1), (-1, 1)]
            if ne and sw and not nw and not se:
                yield x, y, [(-1, -1), (1, 1)]


def build():
    definitions = []
    counts = {}
    for char, rows in GLYPHS.items():
        pixels = {(x, y) for y, row in enumerate(rows)
                  for x, value in enumerate(row) if value == "#"}
        squares = []
        overrides = RECT_OVERRIDES.get(char, {})
        assert overrides.keys() <= pixels
        for x, y in sorted(pixels):
            rx, ry, width, height = overrides.get((x, y), (x, y, 1, 1))
            assert 0 <= rx < rx + width <= 5 and 0 <= ry < ry + height <= 9
            squares.append(
                f'<rect x="{rx}" y="{ry}" width="{width}" height="{height}"/>'
            )
        bridges = []
        for x, y, quadrants in contacts(pixels):
            for sx, sy in quadrants:
                # Concave circular boundary centered at (r,r). These tiny
                # additions connect diagonal squares; no pixel is subtracted.
                bridges.append(
                    f'<path transform="translate({x} {y}) scale({sx} {sy})" '
                    f'd="M0 0 H{RADIUS} A{RADIUS} {RADIUS} 0 0 0 0 {RADIUS} Z"/>'
                )
        counts[char] = {"pixels": len(pixels), "diagonal_contacts": len(bridges) // 2}
        definitions.append(
            f'<g id="glyph-{ord(char)}"><g class="pixels">'
            + "".join(squares) + '</g><g class="menisci">'
            + "".join(bridges) + '</g></g>'
        )

    lines = []
    for label, y in [("Snap Engine", 3), ("Super Rec", 16)]:
        x = 5
        uses = []
        for char in label:
            if char == " ":
                x += 3
            else:
                uses.append(f'<use href="#glyph-{ord(char)}" x="{x}" y="{y}"/>')
                x += 6
        assert x - 1 <= COLS - 5
        lines.append(f'<g aria-label="{label}">' + "".join(uses) + '</g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{COLS*CELL}" height="{ROWS*CELL}" viewBox="0 0 {COLS} {ROWS}" role="img" aria-labelledby="title desc">
  <title id="title">Snap Engine / Super Rec — pixel and surface-tension study</title>
  <desc id="desc">Original 5 by 9 cell glyphs, seven-pixel capitals, five-pixel lowercase, one-pixel stems, and concave bridges at diagonal pixel contacts. Grid-based construction with flat fractional terminals on E/e and small extensions on g/r.</desc>
  <defs>
    <pattern id="grid" width="1" height="1" patternUnits="userSpaceOnUse"><path d="M1 0H0V1" fill="none" stroke="#dedede" stroke-width="0.035"/></pattern>
    {''.join(definitions)}
  </defs>
  <rect width="72" height="28" fill="#ffffff"/>
  <rect width="72" height="28" fill="url(#grid)"/>
  <g id="lettering" fill="#171e24">{''.join(lines)}</g>
</svg>
'''
    ET.fromstring(svg)
    (OUT / "snap-surface-tension.svg").write_text(svg)
    (OUT / "glyphs.json").write_text(json.dumps({
        "cell": [5, 9], "cap_height": 7, "x_height": 5,
        "fillet_radius": RADIUS, "glyphs": GLYPHS,
        "rectangle_overrides": {
            char: [{"cell": list(cell), "rect": list(rect)}
                   for cell, rect in overrides.items()]
            for char, overrides in RECT_OVERRIDES.items()
        },
    }, indent=2) + "\n")
    print(json.dumps({"svg": str(OUT / "snap-surface-tension.svg"), "glyphs": counts}, indent=2))


if __name__ == "__main__":
    build()
