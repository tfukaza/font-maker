from __future__ import annotations

import asyncio

from font_maker.mcp_server import server


def test_mcp_advertises_focused_tools_and_annotations():
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert {
        "create_font_project",
        "open_font_project",
        "get_font_project",
        "upsert_glyphs",
        "suggest_spacing",
        "apply_spacing_proposal",
        "set_kerning",
        "set_ligatures",
        "validate_font_project",
        "shape_text",
        "preview_font",
        "build_font",
    } <= tools.keys()
    assert tools["get_font_project"].annotations.read_only_hint is True
    assert tools["remove_glyphs"].annotations.destructive_hint is True
    assert tools["build_font"].annotations.open_world_hint is False
