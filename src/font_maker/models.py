"""Typed durable and result models for Font Maker."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

GLYPH_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
CODEPOINT_RE = re.compile(r"^U\+([0-9A-F]{4,6})$")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Diagnostic(StrictModel):
    code: str
    severity: Severity
    message: str
    glyph: str | None = None
    rule: str | None = None
    measurements: dict[str, float | int | str] = Field(default_factory=dict)
    suggested_action: str | None = None


class FontMetadata(StrictModel):
    family_name: str = Field(min_length=1, max_length=128)
    style_name: str = Field(default="Regular", min_length=1, max_length=64)
    version: str = "1.000"
    designer: str | None = None
    license_text: str | None = None
    license_url: str | None = None

    @property
    def postscript_name(self) -> str:
        family = re.sub(r"[^A-Za-z0-9]", "", self.family_name)
        style = re.sub(r"[^A-Za-z0-9]", "", self.style_name)
        return f"{family}-{style}"[:63]


class VerticalMetrics(StrictModel):
    units_per_em: Literal[1000, 2048] = 1000
    ascender: int = 800
    cap_height: int = 700
    x_height: int = 500
    baseline: Literal[0] = 0
    descender: int = -200
    line_gap: int = 0

    @model_validator(mode="after")
    def validate_order(self) -> VerticalMetrics:
        if not self.descender < self.baseline < self.x_height <= self.cap_height <= self.ascender:
            raise ValueError(
                "metrics must satisfy descender < baseline < x_height <= cap_height <= ascender"
            )
        if self.ascender - self.descender > self.units_per_em * 2:
            raise ValueError("vertical metrics span is implausibly large")
        return self


class SvgContract(StrictModel):
    view_box: tuple[float, float, float, float] = (0, 0, 1000, 1000)
    y_axis: Literal["down"] = "down"
    baseline_y: float = 800
    scale: float = Field(default=1.0, gt=0, le=100)
    translate_x: float = 0
    translate_y: float = 0

    @model_validator(mode="after")
    def validate_baseline(self) -> SvgContract:
        _, y, _, height = self.view_box
        if not y <= self.baseline_y <= y + height:
            raise ValueError("baseline_y must fall inside the SVG viewBox")
        return self


class GlyphRecord(StrictModel):
    source: str
    codepoints: list[str] = Field(default_factory=list)
    advance_width: int = Field(default=600, ge=0, le=16384)
    left_side_bearing: int | None = Field(default=None, ge=-4096, le=4096)
    right_side_bearing: int | None = Field(default=None, ge=-4096, le=4096)

    @field_validator("source")
    @classmethod
    def source_is_relative(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("glyph source must be a confined relative path")
        return path.as_posix()

    @field_validator("codepoints")
    @classmethod
    def validate_codepoints(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for raw in values:
            value = raw.upper()
            match = CODEPOINT_RE.fullmatch(value)
            integer = int(match.group(1), 16) if match else -1
            if not match or integer > 0x10FFFF or 0xD800 <= integer <= 0xDFFF:
                raise ValueError(f"invalid Unicode codepoint: {raw}")
            normalized.append(value)
        if len(set(normalized)) != len(normalized):
            raise ValueError("duplicate Unicode codepoints on glyph")
        return normalized


class GlyphUpsert(StrictModel):
    name: str
    svg_path: str
    codepoints: list[str] = Field(default_factory=list)
    advance_width: int = Field(default=600, ge=0, le=16384)
    left_side_bearing: int | None = Field(default=None, ge=-4096, le=4096)
    right_side_bearing: int | None = Field(default=None, ge=-4096, le=4096)

    @field_validator("name")
    @classmethod
    def name_is_valid(cls, value: str) -> str:
        return validate_glyph_name(value)


class GlyphMetricsUpdate(StrictModel):
    name: str
    advance_width: int | None = Field(default=None, ge=0, le=16384)
    left_side_bearing: int | None = Field(default=None, ge=-4096, le=4096)
    right_side_bearing: int | None = Field(default=None, ge=-4096, le=4096)

    @field_validator("name")
    @classmethod
    def name_is_valid(cls, value: str) -> str:
        return validate_glyph_name(value)


class KerningPair(StrictModel):
    left: str
    right: str
    value: int = Field(ge=-4096, le=4096)


class KerningData(StrictModel):
    groups: dict[str, list[str]] = Field(default_factory=dict)
    pairs: list[KerningPair] = Field(default_factory=list)


class LigatureRule(StrictModel):
    feature: Literal["liga", "rlig", "dlig"] = "liga"
    sequence: Annotated[list[str], Field(min_length=2, max_length=8)]
    replacement: str


FontFormat = Literal["ttf", "otf", "woff2"]


def _default_formats() -> list[FontFormat]:
    return ["ttf", "otf"]


class BuildOptions(StrictModel):
    formats: list[FontFormat] = Field(default_factory=_default_formats)
    output_dir: str = "build/fonts"
    remove_overlaps: bool = True
    correct_contour_direction: bool = True
    add_extrema: bool = True
    round_coordinates: bool = True


class FontProject(StrictModel):
    schema_version: Literal[1] = 1
    project_id: str
    font: FontMetadata
    metrics: VerticalMetrics = Field(default_factory=VerticalMetrics)
    svg: SvgContract = Field(default_factory=SvgContract)
    references: dict[str, str] = Field(default_factory=dict)
    glyphs: dict[str, GlyphRecord] = Field(default_factory=dict)
    kerning: KerningData = Field(default_factory=KerningData)
    ligatures: list[LigatureRule] = Field(default_factory=list)
    build: BuildOptions = Field(default_factory=BuildOptions)

    @field_validator("glyphs")
    @classmethod
    def validate_glyph_names(cls, glyphs: dict[str, GlyphRecord]) -> dict[str, GlyphRecord]:
        invalid = [
            name for name in glyphs if name in {".", ".."} or not GLYPH_NAME_RE.fullmatch(name)
        ]
        if invalid:
            raise ValueError(f"invalid glyph name(s): {', '.join(invalid)}")
        return glyphs

    @model_validator(mode="after")
    def validate_unicode_uniqueness(self) -> FontProject:
        owners: dict[str, str] = {}
        for name, glyph in self.glyphs.items():
            for codepoint in glyph.codepoints:
                if codepoint in owners and owners[codepoint] != name:
                    raise ValueError(
                        f"codepoint {codepoint} is assigned to both {owners[codepoint]} and {name}"
                    )
                owners[codepoint] = name
        return self


class ProjectRef(StrictModel):
    project_id: str
    revision: str


class Artifact(StrictModel):
    artifact_id: str
    path: str
    mime_type: str
    size: int
    sha256: str
    revision: str


class SpacingChange(StrictModel):
    kind: Literal["glyph_metrics", "kerning"]
    glyph: str | None = None
    left: str | None = None
    right: str | None = None
    before: dict[str, int] = Field(default_factory=dict)
    after: dict[str, int] = Field(default_factory=dict)
    evidence: list[str] = Field(default_factory=list)


class SpacingProposal(StrictModel):
    proposal_id: str
    project_id: str
    base_revision: str
    target_separation: int
    changes: list[SpacingChange]
    preview_strings: list[str] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class MutationResult(StrictModel):
    project_id: str
    revision: str
    changed: list[str] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    suggested_previews: list[str] = Field(default_factory=list)


def validate_glyph_name(name: str) -> str:
    if name in {".", ".."} or not GLYPH_NAME_RE.fullmatch(name):
        raise ValueError(f"invalid glyph name: {name}")
    return name


def codepoint_to_int(codepoint: str) -> int:
    match = CODEPOINT_RE.fullmatch(codepoint.upper())
    if not match:
        raise ValueError(f"invalid codepoint: {codepoint}")
    return int(match.group(1), 16)
