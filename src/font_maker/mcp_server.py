"""Stateful local MCP interface for Font Maker."""

from __future__ import annotations

import base64
from collections.abc import Callable
from typing import Any

from mcp.server import MCPServer
from mcp.types import CallToolResult, ImageContent, TextContent, ToolAnnotations

from .errors import FontMakerError
from .models import (
    GlyphMetricsUpdate,
    GlyphUpsert,
    KerningPair,
    LigatureRule,
    VerticalMetrics,
)
from .service import FontMakerService

INSTRUCTIONS = (
    "Open or create a project before editing. Inspect its current revision and pass that revision "
    "to every mutation. Import SVGs made from the shared template, validate after imports, and "
    "preview the compiled font before export. Spacing suggestions never apply themselves. "
    "FontForge, created by George Williams and maintained by its contributors, is the "
    "GPL-3.0-or-later compilation backend."
)

server = MCPServer(
    name="font-maker",
    title="Font Maker",
    description="A stateful SVG-to-font workshop powered by FontForge.",
    instructions=INSTRUCTIONS,
    version="0.1.0",
)
service = FontMakerService()

READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)
WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)
WRITE_NON_IDEMPOTENT = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)
DESTRUCTIVE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=True,
    open_world_hint=False,
)


def _safe(call: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return call()
    except FontMakerError as exc:
        return {"error": exc.as_dict()}


@server.tool(
    title="Create font project",
    description="Create a durable font project and its shared-coordinate SVG template.",
    annotations=WRITE,
)
def create_font_project(
    path: str,
    family_name: str,
    style_name: str = "Regular",
    metrics: VerticalMetrics | None = None,
    reference_image: str | None = None,
    version: str = "1.000",
    designer: str | None = None,
    license_text: str | None = None,
    license_url: str | None = None,
) -> dict[str, Any]:
    return _safe(
        lambda: service.create_project(
            path,
            family_name,
            style_name,
            metrics,
            reference_image,
            version=version,
            designer=designer,
            license_text=license_text,
            license_url=license_url,
        )
    )


@server.tool(
    title="Open font project",
    description="Open or recover a font project and return its persistent ID and current revision.",
    annotations=READ_ONLY,
)
def open_font_project(path: str) -> dict[str, Any]:
    return _safe(lambda: service.open_project(path))


@server.tool(
    title="Inspect font project",
    description="Inspect the complete normalized project, revision, inventory, and diagnostics.",
    annotations=READ_ONLY,
)
def get_font_project(project_id: str) -> dict[str, Any]:
    return _safe(lambda: service.get_project(project_id))


@server.tool(
    title="Set font metrics",
    description="Set shared vertical metrics without silently rescaling imported glyphs.",
    annotations=WRITE,
)
def set_font_metrics(
    project_id: str, expected_revision: str, metrics: VerticalMetrics
) -> dict[str, Any]:
    return _safe(
        lambda: service.set_font_metrics(project_id, expected_revision, metrics).model_dump(
            mode="json"
        )
    )


@server.tool(
    title="Import SVG glyphs",
    description="Safely normalize and transactionally add or replace a batch of SVG glyphs.",
    annotations=WRITE,
)
def upsert_glyphs(
    project_id: str, expected_revision: str, glyphs: list[GlyphUpsert]
) -> dict[str, Any]:
    return _safe(
        lambda: service.upsert_glyphs(
            project_id,
            expected_revision,
            [item.model_dump(mode="json", exclude_none=True) for item in glyphs],
        ).model_dump(mode="json")
    )


@server.tool(
    title="Remove glyphs",
    description="Remove glyphs; dependent kerning and ligatures require cascade=true.",
    annotations=DESTRUCTIVE,
)
def remove_glyphs(
    project_id: str, expected_revision: str, names: list[str], cascade: bool = False
) -> dict[str, Any]:
    return _safe(
        lambda: service.remove_glyphs(
            project_id, expected_revision, names, cascade=cascade
        ).model_dump(mode="json")
    )


@server.tool(
    title="Set glyph metrics",
    description="Batch-set advances and sidebearings for existing glyphs.",
    annotations=WRITE,
)
def set_glyph_metrics(
    project_id: str, expected_revision: str, updates: list[GlyphMetricsUpdate]
) -> dict[str, Any]:
    return _safe(
        lambda: service.set_glyph_metrics(
            project_id,
            expected_revision,
            [item.model_dump(mode="json", exclude_none=True) for item in updates],
        ).model_dump(mode="json")
    )


@server.tool(
    title="Suggest spacing",
    description="Measure current outlines and return a reviewable, non-mutating spacing proposal.",
    annotations=WRITE_NON_IDEMPOTENT,
)
def suggest_spacing(
    project_id: str,
    glyph_names: list[str] | None = None,
    pair_candidates: list[tuple[str, str]] | None = None,
    target_separation: int | None = None,
) -> dict[str, Any]:
    return _safe(
        lambda: service.suggest_spacing(
            project_id,
            glyph_names=glyph_names,
            pair_candidates=pair_candidates,
            target_separation=target_separation,
        ).model_dump(mode="json")
    )


@server.tool(
    title="Apply spacing proposal",
    description="Apply an explicitly reviewed proposal if its base revision is still current.",
    annotations=WRITE,
)
def apply_spacing_proposal(
    project_id: str, expected_revision: str, proposal_id: str
) -> dict[str, Any]:
    return _safe(
        lambda: service.apply_spacing_proposal(
            project_id, expected_revision, proposal_id
        ).model_dump(mode="json")
    )


@server.tool(
    title="Configure kerning",
    description="Upsert or remove kerning groups and explicit pair/group adjustments.",
    annotations=WRITE,
)
def set_kerning(
    project_id: str,
    expected_revision: str,
    groups: dict[str, list[str]] | None = None,
    upsert_pairs: list[KerningPair] | None = None,
    remove_pairs: list[tuple[str, str]] | None = None,
    remove_groups: list[str] | None = None,
) -> dict[str, Any]:
    return _safe(
        lambda: service.set_kerning(
            project_id,
            expected_revision,
            groups=groups,
            upsert_pairs=upsert_pairs,
            remove_pairs=remove_pairs,
            remove_groups=remove_groups,
        ).model_dump(mode="json")
    )


@server.tool(
    title="Configure ligatures",
    description="Upsert or remove liga, rlig, and dlig glyph-sequence substitutions.",
    annotations=WRITE,
)
def set_ligatures(
    project_id: str,
    expected_revision: str,
    upsert: list[LigatureRule],
    remove: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return _safe(
        lambda: service.set_ligatures(project_id, expected_revision, upsert, remove).model_dump(
            mode="json"
        )
    )


@server.tool(
    title="Validate font project",
    description="Check the manifest, SVG contract, layout rules, and optionally a compiled font.",
    annotations=READ_ONLY,
)
def validate_font_project(project_id: str, temporary_build: bool = False) -> dict[str, Any]:
    return _safe(
        lambda: {
            "project_id": project_id,
            "diagnostics": [
                item.model_dump(mode="json")
                for item in service.validate(project_id, temporary_build=temporary_build)
            ],
        }
    )


@server.tool(
    title="Shape text",
    description="Build and shape text with HarfBuzz, returning glyphs, clusters, advances, and offsets.",
    annotations=WRITE_NON_IDEMPOTENT,
)
def shape_text(
    project_id: str, text: str, features: dict[str, bool] | None = None
) -> dict[str, Any]:
    return _safe(lambda: service.shape(project_id, text, features))


@server.tool(
    title="Preview font",
    description=(
        "Render the compiled font to inline PNG plus SVG and PNG project artifacts; "
        "use pixel_scale=3 for spacing review and 4 for close outline/join inspection."
    ),
    annotations=WRITE_NON_IDEMPOTENT,
    structured_output=False,
)
def preview_font(
    project_id: str,
    text: str,
    features: dict[str, bool] | None = None,
    font_size: int = 96,
    pixel_scale: int = 3,
    guides: bool = True,
) -> CallToolResult:
    try:
        result, png = service.preview(
            project_id,
            text,
            features,
            font_size=max(8, min(font_size, 512)),
            pixel_scale=max(1, min(pixel_scale, 4)),
            guides=guides,
        )
        return CallToolResult(
            structured_content=result,
            content=[
                TextContent(
                    type="text", text=f"Rendered {text!r} at revision {result['revision']}."
                ),
                ImageContent(
                    type="image", data=base64.b64encode(png).decode(), mime_type="image/png"
                ),
            ],
        )
    except FontMakerError as exc:
        return CallToolResult(
            is_error=True,
            structured_content={"error": exc.as_dict()},
            content=[TextContent(type="text", text=f"{exc.code}: {exc.message}")],
        )


@server.tool(
    title="Build font",
    description="Validate and export TTF, OTF, and/or WOFF2 font artifacts.",
    annotations=WRITE_NON_IDEMPOTENT,
)
def build_font(project_id: str, formats: list[str] | None = None) -> dict[str, Any]:
    return _safe(lambda: service.build(project_id, formats))


@server.tool(
    title="Check Font Maker runtime",
    description="Report FontForge availability, version, formats, and attribution.",
    annotations=READ_ONLY,
)
def fontmaker_doctor() -> dict[str, Any]:
    return service.doctor()


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
