from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from font_maker.models import GlyphRecord, SvgContract
from font_maker.store import ProjectStore
from font_maker.svg import normalize_svg

UNICODE_SCALARS = st.integers(min_value=0, max_value=0x10FFFF).filter(
    lambda value: not 0xD800 <= value <= 0xDFFF
)


@given(UNICODE_SCALARS)
def test_unicode_scalar_round_trips(codepoint: int) -> None:
    encoded = f"U+{codepoint:04X}"

    record = GlyphRecord(source="glyphs/test.svg", codepoints=[encoded])

    assert record.codepoints == [encoded]


@given(st.integers(min_value=0xD800, max_value=0xDFFF))
def test_unicode_surrogates_are_rejected(codepoint: int) -> None:
    try:
        GlyphRecord(source="glyphs/test.svg", codepoints=[f"U+{codepoint:04X}"])
    except ValidationError:
        return
    raise AssertionError("surrogate codepoint was accepted")


@given(st.lists(st.sampled_from(["nested", "glyphs"]), min_size=0, max_size=8))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_confined_paths_never_escape_project(tmp_path, segments: list[str]) -> None:
    store = ProjectStore(tmp_path / "font")

    try:
        store.resolve_confined("/".join(["..", *segments, "glyph.svg"]))
    except Exception:
        return
    raise AssertionError("parent traversal path was accepted")


@given(
    x=st.integers(min_value=-200, max_value=200),
    y=st.integers(min_value=-200, max_value=200),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_translation_is_flattened_without_changing_bounds(
    tmp_path, svg_writer, x: int, y: int
) -> None:
    source = svg_writer(
        tmp_path / "translated.svg",
        [],
        extra=(f'<path transform="translate({x} {y})" d="M100 100L200 100L200 300L100 300Z"/>'),
    )

    normalized = normalize_svg(source, SvgContract())

    assert normalized.bounds == (100 + x, 100 + y, 200 + x, 300 + y)
