from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).parents[1]


def test_plugin_manifest_and_mcp_config_are_consistent() -> None:
    plugin = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))

    assert plugin["name"] == "font-maker"
    assert plugin["version"] == "0.1.0"
    assert plugin["license"] == "GPL-3.0-or-later"
    assert "FontForge" in plugin["description"]
    assert plugin["mcpServers"] == "./.mcp.json"
    assert plugin["skills"] == "./skills/"
    assert mcp["mcpServers"]["font-maker"]["args"][-1] == "fontmaker-mcp"
    assert (ROOT / "LICENSE").is_file()
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "George Williams" in notices
    assert "GPL-3.0-or-later" in notices


def test_all_skills_have_valid_discovery_metadata() -> None:
    skill_directories = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    assert {path.name for path in skill_directories} == {
        "font-production-workflow",
        "font-design-metrics",
        "font-outline-qa",
        "font-spacing-kerning",
        "font-ligature-design",
        "font-specimen-review",
        "font-pixel-design",
        "font-serif-design",
        "font-sans-design",
    }

    for directory in skill_directories:
        skill = (directory / "SKILL.md").read_text(encoding="utf-8")
        _, frontmatter, _ = skill.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        discovery = yaml.safe_load(
            (directory / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )

        assert metadata["name"] == directory.name
        assert metadata["description"]
        assert discovery["interface"]["display_name"]
        assert discovery["interface"]["short_description"]
        assert 25 <= len(discovery["interface"]["short_description"]) <= 64
        assert f"${directory.name}" in discovery["interface"]["default_prompt"]
        assert discovery.get("policy", {}).get("allow_implicit_invocation", True) is True


def test_skill_references_resolve_and_are_discoverable() -> None:
    skills = ROOT / "skills"
    documents = list(skills.rglob("*.md"))
    linked: set[Path] = set()
    names = {path.parent.name for path in skills.glob("*/SKILL.md")}
    for document in documents:
        body = document.read_text(encoding="utf-8")
        for name in re.findall(r"\$(font-[a-z-]+)", body):
            assert name in names, (document, name)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
            url = urlsplit(target)
            if url.scheme or not url.path:
                continue
            resolved = (document.parent / unquote(url.path)).resolve()
            assert resolved.is_relative_to(skills), (document, target)
            assert resolved.is_file(), (document, target)
            linked.add(resolved)
    # Every supporting instruction/data file is reachable through an explicit link.
    for reference in skills.glob("*/references/*"):
        if reference.is_file():
            assert reference.resolve() in linked, reference
