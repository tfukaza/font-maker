"""Render reviewable kern OFF/ON sheets from a compiled Font Maker project.

Run with the Python environment containing font_maker. Every case starts pending;
the index is an evidence ledger for a human or image-capable agent to complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
import unicodedata
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from fontTools.ttLib import TTFont

from font_maker.errors import FontMakerError
from font_maker.preview import compose_preview_svg, shape_font, svg_to_png
from font_maker.service import FontMakerService

DEFAULT_GROUPS = {
    "caps": "AV VA WA AW AY YA TA AT LT LV LY",
    "mixed": "To Ta Te Ty Tr Tu Yo Ye Wo We",
    "open-forms": "ra re ro ry rv ar er or yr vr",
    "ligature-context": "fi fl ff ffi ffl",
    "punctuation": "a:a a;a a,a a.a A:A A;A A,A A.A :; ;; ::",
    "words": "AVATAR WAYWARD WATER Typography Hamburgefontsiv HAMBURGEFONTSIV rare radar library",
}
DEFAULT_TEXTS = [
    "Typography Works: Quality, Variety, Rhythm & Style.",
    "Invoice 407 totaled $1,729.50 on 11/07/2026.",
    "Five affable office staff efficiently filed flawless affidavits.",
]

# Small, purpose-drawn proof labels. Rectangles keep labels independent of system
# fonts or the font being assessed. These are UI labels, never imported as glyphs.
LABEL_PIXELS = {
    "0": "111/101/101/101/111",
    "1": "010/110/010/010/111",
    "2": "111/001/111/100/111",
    "3": "111/001/111/001/111",
    "4": "101/101/111/001/001",
    "5": "111/100/111/001/111",
    "6": "111/100/111/101/111",
    "7": "111/001/010/010/010",
    "8": "111/101/111/101/111",
    "9": "111/101/111/001/111",
    "K": "101/101/110/101/101",
    "E": "111/100/110/100/111",
    "R": "110/101/110/101/101",
    "N": "101/111/111/111/101",
    "O": "111/101/101/101/111",
    "F": "111/100/110/100/100",
    "L": "100/100/100/100/111",
    "I": "111/010/010/010/111",
    "G": "111/100/101/101/111",
    "A": "010/101/111/101/101",
    " ": "000/000/000/000/000",
}
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def label_svg(text: str, x: float, y: float) -> ET.Element:
    group = ET.Element(f"{{{NS}}}g", {"fill": "#475569", "aria-label": text})
    ET.SubElement(group, f"{{{NS}}}title").text = text
    for index, character in enumerate(text):
        for row, pixels in enumerate(LABEL_PIXELS[character].split("/")):
            for column, pixel in enumerate(pixels):
                if pixel == "1":
                    ET.SubElement(
                        group,
                        f"{{{NS}}}rect",
                        {
                            "x": str(x + index * 8 + column * 2),
                            "y": str(y + row * 2),
                            "width": "2",
                            "height": "2",
                        },
                    )
    return group


def split_text(text: str, fits: Any) -> list[str]:
    """Prefer word boundaries; overlap a character when a word must be split."""
    remaining = text
    chunks = []
    while remaining:
        if fits(remaining):
            chunks.append(remaining)
            break
        count = 0
        for end in range(1, len(remaining) + 1):
            if not fits(remaining[:end]):
                break
            count = end
        if count < 2:
            raise ValueError(
                "A two-character sample cannot fit; reduce --font-size or increase --sheet-width."
            )
        boundary = remaining.rfind(" ", 0, count + 1)
        if boundary > 1:
            # Include the separator and next glyph on the next line: word-space
            # context remains visible, even though the entire sentence is split.
            chunks.append(remaining[:boundary])
            remaining = remaining[boundary - 1 :]
        else:
            chunks.append(remaining[:count])
            remaining = remaining[count - 1 :]
    return chunks


def collect_sources(
    *,
    pairs: list[str] | None = None,
    texts: list[str] | None = None,
    include_defaults: bool = True,
    left_chars: str | None = None,
    right_chars: str | None = None,
    both_directions: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Build an ordered inventory, retaining every origin of a duplicate sample."""

    def forbidden(character: str) -> bool:
        return character.isspace() or unicodedata.category(character) in {"Cc", "Cf", "Cs"}

    if (left_chars is None) != (right_chars is None):
        raise ValueError("--left-chars and --right-chars must be supplied together.")
    if both_directions and left_chars is None:
        raise ValueError("--both-directions requires --left-chars and --right-chars.")
    for option, characters in (("left-chars", left_chars), ("right-chars", right_chars)):
        if characters is not None and (not characters or any(forbidden(c) for c in characters)):
            raise ValueError(
                f"--{option} requires nonempty characters without whitespace or controls."
            )

    by_text: dict[str, dict[str, Any]] = {}

    def add(group: str, text: str) -> None:
        if text not in by_text:
            by_text[text] = {"group": group, "text": text, "origins": [group]}
        elif group not in by_text[text]["origins"]:
            by_text[text]["origins"].append(group)

    if include_defaults:
        for group, value in DEFAULT_GROUPS.items():
            for text in value.split():
                add(group, text)
        for text in DEFAULT_TEXTS:
            add("sentence", text)
    for pair in pairs or []:
        if len(pair) != 2 or any(forbidden(c) for c in pair):
            raise ValueError(
                "--pair requires exactly two characters without whitespace or controls; use --text for other samples."
            )
        add("custom-pair", pair)

    inventory = None
    if left_chars is not None and right_chars is not None:
        left = "".join(dict.fromkeys(left_chars))
        right = "".join(dict.fromkeys(right_chars))
        forward = [lchar + rchar for lchar in left for rchar in right]
        reverse = [pair[::-1] for pair in forward] if both_directions else []
        for pair in forward:
            add("matrix-forward", pair)
        for pair in reverse:
            add("matrix-reverse", pair)
        inventory = {
            "supplied_left_chars": left_chars,
            "supplied_right_chars": right_chars,
            "left_chars": left,
            "right_chars": right,
            "both_directions": both_directions,
            "forward_pair_count": len(forward),
            "reverse_pair_count": len(reverse),
            "unique_pair_count": len(set(forward + reverse)),
        }
    for text in texts or []:
        add("custom-text", text)
    sources = list(by_text.values())
    if not sources or any(
        not source["text"] or len(source["text"]) > 2000 or any(ord(c) < 32 for c in source["text"])
        for source in sources
    ):
        raise ValueError("Provide nonempty, single-line samples of at most 2000 characters.")
    return sources, inventory


def render_proofs(
    project_path: Path,
    *,
    out: Path | None = None,
    font_size: int = 64,
    pixel_scale: int = 3,
    sheet_width: int = 640,
    rows_per_sheet: int = 4,
    liga: bool = False,
    pairs: list[str] | None = None,
    texts: list[str] | None = None,
    include_defaults: bool = True,
    left_chars: str | None = None,
    right_chars: str | None = None,
    both_directions: bool = False,
) -> dict[str, Any]:
    if not 8 <= font_size <= 512 or not 1 <= pixel_scale <= 4:
        raise ValueError("font_size must be 8-512 and pixel_scale must be 1-4.")
    if not 320 <= sheet_width <= 1200 or not 1 <= rows_per_sheet <= 8:
        raise ValueError("sheet_width must be 320-1200 and rows_per_sheet must be 1-8.")
    sources, inventory = collect_sources(
        pairs=pairs,
        texts=texts,
        include_defaults=include_defaults,
        left_chars=left_chars,
        right_chars=right_chars,
        both_directions=both_directions,
    )
    if out is not None:
        out = out.expanduser().resolve()
        # A proof ledger may already contain a review; never erase it implicitly.
        out.mkdir(parents=True, exist_ok=False)

    service = FontMakerService()
    opened = service.open_project(str(project_path))
    project_id = opened["project_id"]
    store = service.registry.get(project_id)
    with store.locked():
        project = store.load()
        revision = store.revision(project)
        built = service.build(project_id, ["ttf"])
        if built["revision"] != revision:
            raise RuntimeError(
                "Project changed during the proof build; rerun for a consistent revision."
            )
        font_path = store.resolve_confined(built["artifacts"][0]["path"], must_exist=True)
        if out is None:
            parent = store.root / "build" / "previews"
            parent.mkdir(parents=True, exist_ok=True)
            out = Path(tempfile.mkdtemp(prefix=f"kerning-proof-{revision[:12]}-", dir=parent))
        # Snapshot the exact compiled bytes, so later builds cannot alter evidence.
        snapshot = out / "proof-font.ttf"
        snapshot.write_bytes(font_path.read_bytes())
    font_path = snapshot
    with TTFont(font_path) as compiled:
        cmap = compiled.getBestCmap() or {}

    settings = {
        "font_size": font_size,
        "pixel_scale": pixel_scale,
        "sheet_width": sheet_width,
        "rows_per_sheet": rows_per_sheet,
        "sheet_height_target": 650,
        "guides": False,
        "features_off": {"kern": False, "liga": liga, "rlig": True, "dlig": False},
        "features_on": {"kern": True, "liga": liga, "rlig": True, "dlig": False},
    }
    shaping_cache: dict[tuple[str, bool], dict[str, Any]] = {}

    def shape(text: str, kern: bool) -> dict[str, Any]:
        key = (text, kern)
        if key not in shaping_cache:
            shaping_cache[key] = shape_font(
                font_path, text, settings["features_on" if kern else "features_off"]
            )
        return shaping_cache[key]

    column_width = sheet_width // 2 - 12
    margin = max(16, int(font_size * 0.25))

    def fits(text: str, width: int = column_width) -> bool:
        return all(
            shape(text, kern)["total_advance"] * font_size / project.metrics.units_per_em
            + 2 * margin
            <= width
            for kern in (False, True)
        )

    cases: list[dict[str, Any]] = []
    renderable = []
    for source_index, source in enumerate(sources, 1):
        group, source_text = source["group"], source["text"]
        missing = [
            {"character": c, "codepoint": f"U+{ord(c):04X}"}
            for c in dict.fromkeys(source_text)
            if ord(c) not in cmap
        ]
        layout = "side-by-side" if missing or fits(source_text) else "full-width-stacked"
        chunks = (
            [source_text]
            if missing
            else split_text(source_text, lambda text: fits(text, sheet_width - 12))
        )
        for part, text in enumerate(chunks, 1):
            case = {
                "case_id": f"{len(cases) + 1:03d}",
                "group": group,
                "origins": source["origins"],
                "source_id": source_index,
                "source_text": source_text,
                "text": text,
                "part": part,
                "parts": len(chunks),
                "layout": layout if not missing else None,
                "review_status": "pending",
                "observation": "",
                "why_acceptable": "",
                "render_status": "skipped" if missing else "rendered",
                "missing_glyphs": missing,
                "skip_reason": "Missing encoded glyphs; source sample was not substituted with .notdef."
                if missing
                else None,
            }
            cases.append(case)
            if not missing:
                case["shaping"] = {"off": shape(text, False), "on": shape(text, True)}
                if any(g["glyph_id"] == 0 for s in case["shaping"].values() for g in s["glyphs"]):
                    case.update(
                        render_status="skipped",
                        skip_reason="HarfBuzz produced .notdef despite cmap coverage.",
                    )
                else:
                    renderable.append(case)

    sample_height = math.ceil(
        (project.metrics.ascender - project.metrics.descender + project.metrics.line_gap)
        * font_size
        / project.metrics.units_per_em
        + 2 * margin
    )
    row_height = sample_height + 32
    pages: list[list[dict[str, Any]]] = []
    current_page: list[dict[str, Any]] = []
    current_height = 24
    for case in renderable:
        case_height = row_height * (2 if case["layout"] == "full-width-stacked" else 1)
        case["logical_width"] = sheet_width
        case["logical_height"] = case_height
        if current_page and (
            len(current_page) >= rows_per_sheet or current_height + case_height > 650
        ):
            pages.append(current_page)
            current_page = []
            current_height = 24
        current_page.append(case)
        current_height += case_height
    if current_page:
        pages.append(current_page)
    sheets = []
    for rows in pages:
        number = len(sheets) + 1
        height = 24 + sum(case["logical_height"] for case in rows)
        root = ET.Element(
            f"{{{NS}}}svg",
            {
                "width": str(sheet_width),
                "height": str(height),
                "viewBox": f"0 0 {sheet_width} {height}",
            },
        )
        ET.SubElement(
            root, f"{{{NS}}}title"
        ).text = f"{project.font.family_name}: kerning review {number}; revision {revision}"
        ET.SubElement(root, f"{{{NS}}}rect", {"width": "100%", "height": "100%", "fill": "white"})
        case_y = 12
        for row, case in enumerate(rows):
            case["samples"] = {}
            for column, state in enumerate(("off", "on")):
                stacked = case["layout"] == "full-width-stacked"
                x = 6 if stacked else 6 + column * (sheet_width // 2)
                y = case_y + column * row_height if stacked else case_y
                root.append(
                    label_svg(
                        f"{case['case_id']} KERN {state.upper()} LIGA {'ON' if liga else 'OFF'}",
                        x + 10,
                        y,
                    )
                )
                artwork = ET.fromstring(
                    compose_preview_svg(
                        font_path,
                        project,
                        case["shaping"][state],
                        font_size=font_size,
                        guides=False,
                    )
                )
                artwork.set("x", str(x))
                artwork.set("y", str(y + 14))
                root.append(artwork)
                case["samples"][state] = {
                    "x": x,
                    "y": y + 14,
                    "logical_width": int(artwork.attrib["width"]),
                    "logical_height": int(artwork.attrib["height"]),
                    "pixel_width": int(artwork.attrib["width"]) * pixel_scale,
                    "pixel_height": int(artwork.attrib["height"]) * pixel_scale,
                }
            case["sheet"] = f"sheet-{number:03d}.png"
            case["sheet_row"] = row + 1
            case_y += case["logical_height"]
        svg = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        svg_path, png_path = out / f"sheet-{number:03d}.svg", out / f"sheet-{number:03d}.png"
        svg_path.write_bytes(svg)
        png = svg_to_png(svg, pixel_scale=pixel_scale)
        png_path.write_bytes(png)
        sheets.append(
            {
                "svg": svg_path.name,
                "png": png_path.name,
                "case_ids": [case["case_id"] for case in rows],
                "logical_width": sheet_width,
                "logical_height": height,
                "pixel_width": sheet_width * pixel_scale,
                "pixel_height": height * pixel_scale,
                "sha256": hashlib.sha256(png).hexdigest(),
            }
        )

    index = {
        "schema_version": 1,
        "project_id": project_id,
        "revision": revision,
        "family_name": project.font.family_name,
        "project_path": str(store.root),
        "output_path": str(out),
        "settings": settings,
        "font": {
            "path": snapshot.name,
            "sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        },
        "build": built,
        "pair_inventory": inventory,
        "coverage_note": "Defaults are examples. Matrix coverage is exhaustive only for the supplied character sets and directions; discover additional risks from this font's outlines. Pending includes skipped cases. No aesthetic verdict is inferred from numeric shaping.",
        "counts": {
            "sources": len(sources),
            "cases": len(cases),
            "rendered": len(renderable),
            "skipped": len(cases) - len(renderable),
            "pending": len(cases),
            "sheets": len(sheets),
        },
        "sheets": sheets,
        "cases": cases,
    }
    (out / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--out", type=Path, help="New output directory (must not already exist).")
    parser.add_argument("--font-size", type=int, default=64)
    parser.add_argument("--pixel-scale", type=int, default=3)
    parser.add_argument("--sheet-width", type=int, default=640)
    parser.add_argument("--rows-per-sheet", type=int, default=4)
    parser.add_argument(
        "--liga",
        choices=("on", "off"),
        default="off",
        help="Held fixed in both kerning columns; required ligatures stay enabled.",
    )
    parser.add_argument("--pair", action="append", default=[])
    parser.add_argument(
        "--left-chars", help="Characters on the left of a full ordered pair matrix."
    )
    parser.add_argument(
        "--right-chars", help="Characters on the right; required with --left-chars."
    )
    parser.add_argument(
        "--both-directions",
        action="store_true",
        help="Also review each matrix pair reversed; duplicates render once with all origins.",
    )
    parser.add_argument("--text", action="append", default=[])
    parser.add_argument("--no-defaults", action="store_true")
    args = parser.parse_args()
    try:
        index = render_proofs(
            args.project,
            out=args.out,
            font_size=args.font_size,
            pixel_scale=args.pixel_scale,
            sheet_width=args.sheet_width,
            rows_per_sheet=args.rows_per_sheet,
            liga=args.liga == "on",
            pairs=args.pair,
            left_chars=args.left_chars,
            right_chars=args.right_chars,
            both_directions=args.both_directions,
            texts=args.text,
            include_defaults=not args.no_defaults,
        )
    except (ValueError, OSError, FontMakerError, RuntimeError) as exc:
        parser.exit(1, f"Kerning proofs failed: {exc}\n")
    print(
        json.dumps(
            {
                "index": str(Path(index["output_path"]) / "index.json"),
                "revision": index["revision"],
                "counts": index["counts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
