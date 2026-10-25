import asyncio

from mcp.types import CallToolResult

from font_maker.mcp_server import APP_URI, server


def test_font_designer_tool_is_bound_to_mcp_app_resource() -> None:
    tool = server._tool_manager.get_tool("open_font_designer")
    resources = server._resource_manager.list_resources()

    assert tool is not None
    assert tool.meta == {"ui": {"resourceUri": APP_URI, "visibility": ["model", "app"]}}
    assert len(resources) == 1
    assert str(resources[0].uri) == APP_URI
    assert resources[0].mime_type == "text/html;profile=mcp-app"
    assert "Font Maker" in resources[0].text


def test_open_font_designer_returns_ui_ready_structured_content() -> None:
    result = asyncio.run(
        server._tool_manager.call_tool(
            "open_font_designer",
            {"sample_text": "Signal Lost", "mode": "guided"},
            None,  # type: ignore[arg-type]
            convert_result=True,
        )
    )

    assert isinstance(result, CallToolResult)
    assert result.structured_content is not None
    assert result.structured_content["brief"]["sample_text"] == "Signal Lost"
    assert result.structured_content["brief"]["mode"] == "guided"
