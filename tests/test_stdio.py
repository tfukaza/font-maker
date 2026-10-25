from __future__ import annotations

from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_stdio_server_initializes_and_calls_doctor() -> None:
    project_root = Path(__file__).parents[1]
    parameters = StdioServerParameters(
        command=str(project_root / ".venv" / "bin" / "fontmaker-mcp"),
        cwd=project_root,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        initialized = await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("fontmaker_doctor", {})

    assert initialized.server_info.name == "font-maker"
    assert any(tool.name == "preview_font" for tool in tools.tools)
    assert result.is_error is False
    assert result.structured_content["fontforge"]["available"] is True


@pytest.mark.asyncio
async def test_stdio_project_state_survives_restart_and_rejects_stale_write(
    tmp_path, svg_writer
) -> None:
    project_root = Path(__file__).parents[1]
    project_path = tmp_path / "stdio-font"
    glyph_path = svg_writer(
        tmp_path / "A.svg", ["M80 800L300 100L520 800L430 800L300 500L170 800Z"]
    )
    parameters = StdioServerParameters(
        command=str(project_root / ".venv" / "bin" / "fontmaker-mcp"),
        cwd=project_root,
    )

    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        created_result = await session.call_tool(
            "create_font_project",
            {"path": str(project_path), "family_name": "STDIO Sans"},
        )
        created = created_result.structured_content
        imported_result = await session.call_tool(
            "upsert_glyphs",
            {
                "project_id": created["project_id"],
                "expected_revision": created["revision"],
                "glyphs": [
                    {
                        "name": "A",
                        "svg_path": str(glyph_path),
                        "codepoints": ["U+0041"],
                        "advance_width": 600,
                    }
                ],
            },
        )
        imported = imported_result.structured_content
        stale_result = await session.call_tool(
            "set_glyph_metrics",
            {
                "project_id": created["project_id"],
                "expected_revision": created["revision"],
                "updates": [{"name": "A", "advance_width": 620}],
            },
        )

    assert stale_result.structured_content["error"]["code"] == "REVISION_CONFLICT"
    assert stale_result.structured_content["error"]["details"]["changed_sections"]

    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as restarted,
    ):
        await restarted.initialize()
        reopened_result = await restarted.call_tool(
            "open_font_project", {"path": str(project_path)}
        )

    reopened = reopened_result.structured_content
    assert reopened["project_id"] == created["project_id"]
    assert reopened["revision"] == imported["revision"]
