"""Thin command-line adapter over the Font Maker service."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .errors import FontMakerError
from .service import FontMakerService

app = typer.Typer(
    name="fontmaker",
    help="Build fonts from project-aligned SVG glyphs using FontForge.",
    no_args_is_help=True,
)
console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(
            "Font Maker 0.1.0 — powered by FontForge (George Williams and contributors), "
            "GPL-3.0-or-later"
        )
        raise typer.Exit()


@app.callback()
def root_options(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and FontForge attribution",
        ),
    ] = False,
) -> None:
    """Font Maker command-line entry point."""
    _ = version


def _json(value: object) -> None:
    typer.echo(json.dumps(value, indent=2, sort_keys=True, default=str))


def _open(path: Path) -> tuple[FontMakerService, str]:
    service = FontMakerService()
    opened = service.open_project(str(path))
    return service, str(opened["project_id"])


@app.command()
def doctor() -> None:
    """Report backend availability and FontForge attribution."""
    _json(FontMakerService().doctor())


@app.command("init")
def initialize(
    path: Annotated[Path, typer.Argument(help="Directory for the new font project")],
    family: Annotated[str, typer.Option("--family", help="Font family name")],
    style: Annotated[str, typer.Option("--style", help="Font style name")] = "Regular",
    reference: Annotated[
        Path | None, typer.Option("--reference", help="Optional concept image")
    ] = None,
    version: Annotated[str, typer.Option("--version", help="Generated font version")] = "1.000",
    designer: Annotated[str | None, typer.Option("--designer")] = None,
    font_license: Annotated[
        str | None, typer.Option("--font-license", help="License text for the generated font")
    ] = None,
    font_license_url: Annotated[str | None, typer.Option("--font-license-url")] = None,
) -> None:
    """Create a font project and its canonical SVG template."""
    result = FontMakerService().create_project(
        str(path),
        family,
        style,
        reference_image=str(reference) if reference else None,
        version=version,
        designer=designer,
        license_text=font_license,
        license_url=font_license_url,
    )
    _json(result)


@app.command()
def check(
    path: Annotated[Path, typer.Argument(help="Font project directory")],
    build: Annotated[bool, typer.Option("--build", help="Also compile a temporary TTF")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit machine-readable JSON (the default output)")
    ] = False,
) -> None:
    """Validate a project, optionally including the native backend."""
    service, project_id = _open(path)
    _ = json_output
    result = [
        item.model_dump(mode="json") for item in service.validate(project_id, temporary_build=build)
    ]
    _json({"project_id": project_id, "diagnostics": result})
    if any(item["severity"] == "error" for item in result):
        raise typer.Exit(1)


@app.command()
def shape(
    path: Annotated[Path, typer.Argument(help="Font project directory")],
    text: Annotated[str, typer.Option("--text", help="Text to shape")],
    no_kern: Annotated[bool, typer.Option("--no-kern")] = False,
    no_liga: Annotated[bool, typer.Option("--no-liga")] = False,
) -> None:
    """Build and shape text with the generated font."""
    service, project_id = _open(path)
    _json(service.shape(project_id, text, {"kern": not no_kern, "liga": not no_liga}))


@app.command()
def preview(
    path: Annotated[Path, typer.Argument(help="Font project directory")],
    text: Annotated[str, typer.Option("--text", help="Text to render")],
    out: Annotated[Path, typer.Option("--out", help="Destination PNG")],
    font_size: Annotated[int, typer.Option("--font-size", min=8, max=512)] = 96,
    pixel_scale: Annotated[int, typer.Option("--scale", min=1, max=4)] = 3,
    guides: Annotated[bool, typer.Option("--guides/--no-guides")] = True,
) -> None:
    """Render compiled text and copy the PNG to the requested path."""
    service, project_id = _open(path)
    result, _ = service.preview(
        project_id, text, font_size=font_size, pixel_scale=pixel_scale, guides=guides
    )
    store = service.registry.get(project_id)
    png = next(item for item in result["artifacts"] if item["mime_type"] == "image/png")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(store.resolve_confined(png["path"], must_exist=True), out)
    result["copied_to"] = str(out.resolve())
    _json(result)


@app.command()
def build(
    path: Annotated[Path, typer.Argument(help="Font project directory")],
    formats: Annotated[
        list[str] | None,
        typer.Option("--format", help="Repeat for ttf, otf, or woff2"),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit machine-readable JSON (the default output)")
    ] = False,
) -> None:
    """Validate and export installable font artifacts."""
    service, project_id = _open(path)
    _ = json_output
    _json(service.build(project_id, formats))


def main() -> None:
    try:
        app()
    except FontMakerError as exc:
        console.print(f"[red]{exc.code}[/red]: {exc.message}")
        if exc.details:
            console.print_json(data=exc.details)
        raise typer.Exit(1) from exc


if __name__ == "__main__":
    main()
