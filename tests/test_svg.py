from __future__ import annotations

from pathlib import Path

import pytest

from font_maker.errors import FontMakerError
from font_maker.models import SvgContract
from font_maker.svg import font_space_recordings, normalize_svg


def test_normalize_strips_guides_and_flattens_transform(tmp_path, svg_writer):
    source = svg_writer(
        tmp_path / "A.svg",
        [],
        extra='<g transform="translate(10 20)"><rect x="100" y="100" width="200" height="300"/></g>',
    )
    normalized = normalize_svg(source, SvgContract())

    text = normalized.content.decode()
    assert "fontmaker-guides" not in text
    assert "transform=" not in text
    assert "<path" in text
    assert normalized.bounds == pytest.approx((110, 120, 310, 420))


def test_transform_parser_rejects_unparsed_garbage(tmp_path, svg_writer):
    source = svg_writer(
        tmp_path / "bad-transform.svg",
        [],
        extra='<path transform="translate(10) garbage" d="M0 0L10 0L10 10Z"/>',
    )
    with pytest.raises(FontMakerError, match="Unsupported transform"):
        normalize_svg(source, SvgContract())


def test_font_space_y_flip_happens_once(tmp_path, svg_writer):
    source = svg_writer(tmp_path / "H.svg", ["M100 100L200 100L200 800L100 800Z"])
    recordings = font_space_recordings(source, SvgContract())
    points = [point for _, values in recordings[0].value for point in values]
    ys = [point[1] for point in points]

    assert min(ys) == 0
    assert max(ys) == 700


def test_shipped_template_can_be_used_with_ignored_guide_labels(tmp_path):
    template = Path(__file__).parents[1] / "templates" / "glyph-template.svg"
    source = tmp_path / "from-template.svg"
    content = template.read_text(encoding="utf-8").replace(
        '<g id="glyph" fill="#000000" />',
        '<g id="glyph" fill="#000000"><path d="M100 100L200 100L200 800L100 800Z"/></g>',
    )
    source.write_text(content, encoding="utf-8")

    normalized = normalize_svg(source, SvgContract())

    assert normalized.operation_count > 0


def test_active_content_is_rejected_even_outside_glyph(tmp_path, svg_writer):
    source = svg_writer(tmp_path / "active.svg", ["M0 0L10 0L10 10Z"])
    content = source.read_text(encoding="utf-8").replace("<svg ", '<svg onload="alert(1)" ')
    source.write_text(content, encoding="utf-8")

    with pytest.raises(FontMakerError, match="Unsafe onload"):
        normalize_svg(source, SvgContract())


@pytest.mark.parametrize(
    "extra",
    [
        '<path d="M0 0L10 10"/>',
        '<path d="M0 0L10 0L10 10Z" stroke="black"/>',
        '<image href="https://example.com/a.png"/>',
        '<text x="10" y="10">A</text>',
        '<path d="M0 0L10 0L10 10Z" fill="white"/>',
        '<path d="M0 0L10 0L10 10Z" fill-rule="evenodd"/>',
        '<path d="M0 0L10 0L10 10Z" opacity="0"/>',
    ],
)
def test_unsafe_or_ambiguous_svg_is_rejected(tmp_path, svg_writer, extra):
    source = svg_writer(tmp_path / "bad.svg", [], extra=extra)
    with pytest.raises(FontMakerError):
        normalize_svg(source, SvgContract())
