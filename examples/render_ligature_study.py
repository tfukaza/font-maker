"""Package the experimental font into an offline, revision-specific specimen."""

import base64
import hashlib
import json
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

from font_maker.preview import compose_preview_svg, shape_font, svg_to_png
from font_maker.service import FontMakerService

VERDICTS = {
    "ct": (
        "Factory actor",
        "Readable in words, but the enclosed top can feel d-like at small size.",
    ),
    "tt": (
        "letter little",
        "Strong candidate: two ascenders and separate feet preserve both letters.",
    ),
    "st": ("system pasta", "Promising: a shared upper rail with a recognizable s and distinct t."),
    "ra": ("rare graphic", "Not recommended in this form: the join closes the a's upper opening."),
    "oo": ("loop moon", "Emblem-like experiment: two counters become a compact spectacles shape."),
}


def render(root: Path) -> None:
    report = json.loads((root / "report.json").read_text())
    font_path = root / "project/build/fonts/SuperPixelLigatureStudy-Regular.woff2"
    font_bytes = font_path.read_bytes()
    with TTFont(font_path) as font:
        codepoints = sorted(font.getBestCmap())
    data = dict(
        font=base64.b64encode(font_bytes).decode(),
        codepoints=codepoints,
        revision=report["revision"],
        sha256=hashlib.sha256(font_bytes).hexdigest(),
        candidates=[dict(sequence=s, words=v[0], verdict=v[1]) for s, v in VERDICTS.items()],
    )
    template = Path(__file__).with_name("ligature_specimen.html").read_text()
    (root / "specimen.html").write_text(template.replace("__STUDY_DATA__", json.dumps(data)))
    service = FontMakerService()
    opened = service.open_project(str(root / "project"))
    _, project = service._store_project(opened["project_id"])
    ttf = root / "project/build/fonts/SuperPixelLigatureStudy-Regular.ttf"
    for sequence in VERDICTS:
        for label, text, size, scale in [
            ("detail", sequence, 180, 4),
            ("boundary", "a" + sequence + "o " + sequence * 2 + ".", 64, 3),
        ]:
            shaping = shape_font(ttf, text, {"kern": True, "liga": False, "dlig": True})
            svg = compose_preview_svg(ttf, project, shaping, font_size=size, guides=False)
            if isinstance(svg, str):
                svg = svg.encode()
            stem = root / "proofs" / (sequence + "-" + label)
            stem.with_suffix(".svg").write_bytes(svg)
            stem.with_suffix(".png").write_bytes(svg_to_png(svg, pixel_scale=scale))


if __name__ == "__main__":
    render(Path(sys.argv[1]).resolve())
