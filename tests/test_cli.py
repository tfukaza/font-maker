from __future__ import annotations

import json

from typer.testing import CliRunner

from font_maker.cli import app

runner = CliRunner()


def test_version_includes_fontforge_credit() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "Font Maker 0.1.0" in result.stdout
    assert "FontForge" in result.stdout
    assert "GPL-3.0-or-later" in result.stdout


def test_init_and_check_accept_documented_json_flag(tmp_path) -> None:
    project = tmp_path / "cli-font"
    initialized = runner.invoke(
        app,
        ["init", str(project), "--family", "CLI Sans", "--font-license", "OFL-1.1"],
    )
    checked = runner.invoke(app, ["check", str(project), "--json"])

    assert initialized.exit_code == 0
    assert checked.exit_code == 0
    payload = json.loads(checked.stdout)
    assert payload["diagnostics"] == []
