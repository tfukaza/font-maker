"""Atomic, Git-friendly project persistence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from filelock import FileLock
from ruamel.yaml import YAML

from .errors import FontMakerError, RevisionConflict
from .models import FontMetadata, FontProject, SvgContract, VerticalMetrics
from .template import render_glyph_template

MANIFEST_NAME = "font.yaml"


class ProjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self.manifest_path = self.root / MANIFEST_NAME
        self.state_dir = self.root / ".fontmaker"
        self._yaml = YAML(typ="safe")
        self._yaml.default_flow_style = False

    @classmethod
    def create(
        cls,
        root: Path,
        family_name: str,
        style_name: str = "Regular",
        metrics: VerticalMetrics | None = None,
        reference_image: Path | None = None,
        *,
        version: str = "1.000",
        designer: str | None = None,
        license_text: str | None = None,
        license_url: str | None = None,
    ) -> tuple[ProjectStore, FontProject]:
        store = cls(root)
        if store.manifest_path.exists():
            raise FontMakerError("PROJECT_EXISTS", f"A font project already exists at {store.root}")
        store.root.mkdir(parents=True, exist_ok=True)
        for path in (
            store.root / "glyphs",
            store.root / "references",
            store.root / "build" / "fonts",
            store.root / "build" / "previews",
            store.state_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

        actual_metrics = metrics or VerticalMetrics()
        svg = SvgContract(
            view_box=(
                0,
                0,
                actual_metrics.units_per_em,
                max(actual_metrics.units_per_em, actual_metrics.ascender - actual_metrics.descender),
            ),
            baseline_y=actual_metrics.ascender,
        )
        project = FontProject(
            project_id=str(uuid.uuid4()),
            font=FontMetadata(
                family_name=family_name,
                style_name=style_name,
                version=version,
                designer=designer,
                license_text=license_text,
                license_url=license_url,
            ),
            metrics=actual_metrics,
            svg=svg,
        )
        if reference_image is not None:
            try:
                source = reference_image.expanduser().resolve(strict=True)
            except OSError as exc:
                raise FontMakerError(
                    "INVALID_REFERENCE", f"Reference does not exist: {reference_image}"
                ) from exc
            if not source.is_file():
                raise FontMakerError("INVALID_REFERENCE", f"Reference is not a file: {source}")
            destination = store.root / "references" / source.name
            shutil.copy2(source, destination)
            project.references["concept"] = destination.relative_to(store.root).as_posix()

        store._write_project_unlocked(project)
        store.write_template(project)
        return store, project

    def load(self) -> FontProject:
        if not self.manifest_path.is_file():
            raise FontMakerError("PROJECT_NOT_FOUND", f"No {MANIFEST_NAME} found at {self.root}")
        try:
            data = self._yaml.load(self.manifest_path.read_text(encoding="utf-8"))
            return FontProject.model_validate(data)
        except FontMakerError:
            raise
        except Exception as exc:
            raise FontMakerError(
                "INVALID_MANIFEST", f"Cannot load {self.manifest_path}: {exc}"
            ) from exc

    def resolve_confined(self, relative_path: str, *, must_exist: bool = False) -> Path:
        candidate = (self.root / relative_path).resolve(strict=must_exist)
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise FontMakerError(
                "UNSAFE_PATH", f"Path escapes the font project: {relative_path}"
            ) from exc
        return candidate

    def revision(self, project: FontProject | None = None) -> str:
        actual = project or self.load()
        digest = hashlib.sha256()
        canonical = json.dumps(
            actual.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ).encode()
        digest.update(canonical)
        referenced = [glyph.source for glyph in actual.glyphs.values()]
        referenced.extend(actual.references.values())
        for relative in sorted(set(referenced)):
            path = self.resolve_confined(relative)
            digest.update(relative.encode())
            if path.is_file():
                digest.update(path.read_bytes())
            else:
                digest.update(b"<missing>")
        return digest.hexdigest()

    def assert_revision(self, expected_revision: str, project: FontProject | None = None) -> None:
        current = self.revision(project)
        if expected_revision != current:
            raise RevisionConflict(expected_revision, current)

    @contextmanager
    def locked(self, timeout: float = 10) -> Iterator[None]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        lock = FileLock(self.state_dir / "project.lock", timeout=timeout)
        with lock:
            yield

    def save(self, project: FontProject, expected_revision: str) -> str:
        with self.locked():
            on_disk = self.load()
            self.assert_revision(expected_revision, on_disk)
            self._write_project_unlocked(project)
            return self.revision(project)

    def _write_project_unlocked(self, project: FontProject) -> None:
        payload = project.model_dump(mode="json", exclude_none=True)
        fd, temp_name = tempfile.mkstemp(prefix=".font.", suffix=".yaml", dir=self.root)
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            with temp_path.open("w", encoding="utf-8") as stream:
                yaml = YAML()
                yaml.default_flow_style = False
                yaml.indent(mapping=2, sequence=4, offset=2)
                yaml.dump(payload, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, self.manifest_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def write_template(self, project: FontProject) -> Path:
        path = self.root / "glyph-template.svg"
        content = render_glyph_template(project.font, project.metrics, project.svg)
        self.atomic_write(path, content.encode())
        return path

    def atomic_write(self, destination: Path, data: bytes) -> None:
        destination = destination.resolve()
        try:
            destination.relative_to(self.root)
        except ValueError as exc:
            raise FontMakerError(
                "UNSAFE_PATH", f"Write escapes font project: {destination}"
            ) from exc
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, destination)
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def summary(self, project: FontProject | None = None) -> dict[str, Any]:
        actual = project or self.load()
        return {
            "path": str(self.root),
            "project_id": actual.project_id,
            "revision": self.revision(actual),
            "family_name": actual.font.family_name,
            "style_name": actual.font.style_name,
            "glyph_count": len(actual.glyphs),
            "kerning_pair_count": len(actual.kerning.pairs),
            "ligature_count": len(actual.ligatures),
        }


class ProjectRegistry:
    """Process-local project handles backed by durable project UUIDs."""

    def __init__(self) -> None:
        self._stores: dict[str, ProjectStore] = {}

    def register(self, store: ProjectStore, project: FontProject | None = None) -> str:
        actual = project or store.load()
        self._stores[actual.project_id] = store
        return actual.project_id

    def open(self, path: Path) -> tuple[ProjectStore, FontProject]:
        store = ProjectStore(path)
        project = store.load()
        self.register(store, project)
        return store, project

    def get(self, project_id: str) -> ProjectStore:
        try:
            return self._stores[project_id]
        except KeyError as exc:
            raise FontMakerError(
                "PROJECT_NOT_OPEN",
                "The project is not open in this server process. Call open_font_project first.",
                project_id=project_id,
            ) from exc
