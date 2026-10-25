"""The single application service used by MCP and CLI adapters."""

from __future__ import annotations

import hashlib
import shutil
import statistics
import time
import uuid
from pathlib import Path
from typing import Any

from fontTools.pens.boundsPen import BoundsPen

from .backend import (
    SUPPORTED_FONTFORGE_VERSION,
    build_font,
    find_fontforge,
    fontforge_version,
    suggest_spacing_with_fontforge,
)
from .cache import ProjectCache
from .errors import FontMakerError, RevisionConflict
from .models import (
    Diagnostic,
    FontProject,
    GlyphRecord,
    KerningPair,
    LigatureRule,
    MutationResult,
    Severity,
    SpacingChange,
    SpacingProposal,
    VerticalMetrics,
    validate_glyph_name,
)
from .preview import shape_font, write_preview
from .store import ProjectRegistry, ProjectStore
from .svg import font_space_recordings, normalize_svg

DEFAULT_RISK_PAIRS = (
    "AV",
    "AW",
    "AT",
    "AY",
    "FA",
    "LT",
    "PA",
    "Ta",
    "Te",
    "To",
    "Tr",
    "Tu",
    "Va",
    "Vo",
    "Wa",
    "Wo",
    "Ya",
    "Yo",
)
MAX_BATCH_ITEMS = 512
MAX_PREVIEW_TEXT_LENGTH = 4096


def _canonical_glyph_source(name: str) -> str:
    """Return a source path that stays unique on case-insensitive filesystems."""

    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return f"glyphs/{digest}.svg"


class FontMakerService:
    def __init__(self, registry: ProjectRegistry | None = None) -> None:
        self.registry = registry or ProjectRegistry()

    def create_project(
        self,
        path: str,
        family_name: str,
        style_name: str = "Regular",
        metrics: VerticalMetrics | None = None,
        reference_image: str | None = None,
        *,
        version: str = "1.000",
        designer: str | None = None,
        license_text: str | None = None,
        license_url: str | None = None,
    ) -> dict[str, Any]:
        store, project = ProjectStore.create(
            Path(path),
            family_name,
            style_name,
            metrics,
            Path(reference_image) if reference_image else None,
            version=version,
            designer=designer,
            license_text=license_text,
            license_url=license_url,
        )
        self.registry.register(store, project)
        return {
            **store.summary(project),
            "template_path": str(store.root / "glyph-template.svg"),
        }

    def open_project(self, path: str) -> dict[str, Any]:
        store, project = self.registry.open(Path(path))
        return {
            **store.summary(project),
            "capabilities": self.doctor(),
        }

    def get_project(self, project_id: str) -> dict[str, Any]:
        store = self.registry.get(project_id)
        project = store.load()
        return {
            **store.summary(project),
            "project": project.model_dump(mode="json"),
            "artifacts": ProjectCache(store.state_dir).list_artifacts(),
            "diagnostics": [item.model_dump(mode="json") for item in self.validate(project_id)],
        }

    def _store_project(self, project_id: str) -> tuple[ProjectStore, FontProject]:
        store = self.registry.get(project_id)
        return store, store.load()

    def set_font_metrics(
        self, project_id: str, expected_revision: str, metrics: VerticalMetrics
    ) -> MutationResult:
        store, project = self._store_project(project_id)
        if project.glyphs and metrics.units_per_em != project.metrics.units_per_em:
            raise FontMakerError(
                "UPM_CHANGE_REQUIRES_EMPTY_PROJECT",
                "Changing units-per-em after glyph import would silently rescale the design.",
            )
        updated = project.model_copy(deep=True)
        updated.metrics = metrics
        if not project.glyphs:
            updated.svg.view_box = (
                0,
                0,
                metrics.units_per_em,
                max(metrics.units_per_em, metrics.ascender - metrics.descender),
            )
            updated.svg.baseline_y = metrics.ascender
        revision = store.save(updated, expected_revision)
        store.write_template(updated)
        return MutationResult(
            project_id=project_id,
            revision=revision,
            changed=["metrics", "glyph-template.svg"],
            suggested_previews=["HHOHHO", "nnonn", "Hoxp"],
        )

    def upsert_glyphs(
        self,
        project_id: str,
        expected_revision: str,
        glyphs: list[dict[str, Any]],
    ) -> MutationResult:
        if not glyphs or len(glyphs) > MAX_BATCH_ITEMS:
            raise FontMakerError(
                "INVALID_BATCH_SIZE",
                f"Glyph imports require 1 to {MAX_BATCH_ITEMS} items per transaction.",
            )
        store, project = self._store_project(project_id)
        store.assert_revision(expected_revision, project)
        prepared: list[tuple[str, GlyphRecord, bytes, tuple[str, ...]]] = []
        seen_names: set[str] = set()
        for item in glyphs:
            name = validate_glyph_name(str(item["name"]))
            if name in seen_names:
                raise FontMakerError(
                    "DUPLICATE_GLYPH_IN_BATCH", f"Glyph {name} occurs more than once in the batch."
                )
            seen_names.add(name)
            try:
                source = Path(str(item["svg_path"])).expanduser().resolve(strict=True)
            except OSError as exc:
                raise FontMakerError(
                    "GLYPH_SOURCE_NOT_FOUND", f"Cannot read glyph source for {name}."
                ) from exc
            if not source.is_file():
                raise FontMakerError(
                    "GLYPH_SOURCE_NOT_FOUND", f"Glyph source for {name} is not a file."
                )
            normalized = normalize_svg(source, project.svg)
            glyph_source = _canonical_glyph_source(name)
            record = GlyphRecord(
                source=glyph_source,
                codepoints=item.get("codepoints", []),
                advance_width=item.get("advance_width", 600),
                left_side_bearing=item.get("left_side_bearing"),
                right_side_bearing=item.get("right_side_bearing"),
            )
            prepared.append((name, record, normalized.content, normalized.fixes))

        updated = project.model_copy(deep=True)
        for name, record, _, _ in prepared:
            updated.glyphs[name] = record
        updated = FontProject.model_validate(updated.model_dump(mode="json"))
        changed = []
        diagnostics: list[Diagnostic] = []
        with store.locked():
            current = store.load()
            store.assert_revision(expected_revision, current)
            backups: dict[Path, bytes | None] = {}
            try:
                for name, record, content, fixes in prepared:
                    destination = store.resolve_confined(record.source)
                    backups[destination] = (
                        destination.read_bytes() if destination.exists() else None
                    )
                    store.atomic_write(destination, content)
                    changed.append(record.source)
                    diagnostics.append(
                        Diagnostic(
                            code="SVG_NORMALIZED",
                            severity=Severity.INFO,
                            message="; ".join(fixes),
                            glyph=name,
                        )
                    )
                store._write_project_unlocked(updated)
            except Exception:
                for destination, backup in backups.items():
                    if backup is None:
                        destination.unlink(missing_ok=True)
                    else:
                        store.atomic_write(destination, backup)
                raise
        return MutationResult(
            project_id=project_id,
            revision=store.revision(updated),
            changed=[*changed, "font.yaml"],
            diagnostics=diagnostics,
            suggested_previews=["HHOHHO", "nnonn", "AVATAR", "affine office"],
        )

    def remove_glyphs(
        self,
        project_id: str,
        expected_revision: str,
        names: list[str],
        *,
        cascade: bool = False,
    ) -> MutationResult:
        if not names or len(names) > MAX_BATCH_ITEMS:
            raise FontMakerError(
                "INVALID_BATCH_SIZE",
                f"Glyph removal requires 1 to {MAX_BATCH_ITEMS} names.",
            )
        store, project = self._store_project(project_id)
        requested = {validate_glyph_name(name) for name in names}
        unknown = sorted(requested - project.glyphs.keys())
        if unknown:
            raise FontMakerError("GLYPH_NOT_FOUND", f"Unknown glyph(s): {', '.join(unknown)}")
        dependencies: list[str] = []
        affected_groups = {
            group
            for group, members in project.kerning.groups.items()
            if requested.intersection(members)
        }
        dependencies.extend(f"kern-group:{group}" for group in sorted(affected_groups))
        for rule in project.ligatures:
            if requested.intersection((*rule.sequence, rule.replacement)):
                dependencies.append(f"{rule.feature}:{'+'.join(rule.sequence)}")
        for pair in project.kerning.pairs:
            if (
                pair.left in requested
                or pair.right in requested
                or (pair.left.startswith("@") and pair.left[1:] in affected_groups)
                or (pair.right.startswith("@") and pair.right[1:] in affected_groups)
            ):
                dependencies.append(f"kern:{pair.left}/{pair.right}")
        if dependencies and not cascade:
            raise FontMakerError(
                "GLYPH_HAS_DEPENDENCIES",
                "Glyph removal would invalidate layout rules; repeat with cascade=true.",
                dependencies=dependencies,
            )

        updated = project.model_copy(deep=True)
        removed_sources = {name: updated.glyphs[name].source for name in requested}
        for name in requested:
            del updated.glyphs[name]
        updated.kerning.pairs = [
            pair
            for pair in updated.kerning.pairs
            if pair.left not in requested and pair.right not in requested
        ]
        deleted_groups: set[str] = set()
        for group, members in list(updated.kerning.groups.items()):
            remaining = [name for name in members if name not in requested]
            if remaining:
                updated.kerning.groups[group] = remaining
            else:
                del updated.kerning.groups[group]
                deleted_groups.add(group)
        updated.kerning.pairs = [
            pair
            for pair in updated.kerning.pairs
            if not (pair.left.startswith("@") and pair.left[1:] in deleted_groups)
            and not (pair.right.startswith("@") and pair.right[1:] in deleted_groups)
        ]
        updated.ligatures = [
            rule
            for rule in updated.ligatures
            if not requested.intersection((*rule.sequence, rule.replacement))
        ]
        revision = store.save(updated, expected_revision)
        trash = store.state_dir / "trash"
        trash.mkdir(parents=True, exist_ok=True)
        stamp = int(time.time())
        for name in requested:
            source = store.resolve_confined(removed_sources[name])
            if source.exists():
                shutil.move(source, trash / f"{stamp}-{source.name}")
        return MutationResult(
            project_id=project_id,
            revision=revision,
            changed=[f"removed:{name}" for name in sorted(requested)],
            diagnostics=[
                Diagnostic(
                    code="GLYPHS_MOVED_TO_TRASH",
                    severity=Severity.INFO,
                    message="Removed SVG files remain recoverable under .fontmaker/trash.",
                )
            ],
        )

    def set_glyph_metrics(
        self,
        project_id: str,
        expected_revision: str,
        updates: list[dict[str, Any]],
    ) -> MutationResult:
        if not updates or len(updates) > MAX_BATCH_ITEMS:
            raise FontMakerError(
                "INVALID_BATCH_SIZE",
                f"Metric updates require 1 to {MAX_BATCH_ITEMS} items.",
            )
        store, project = self._store_project(project_id)
        updated = project.model_copy(deep=True)
        changed = []
        for item in updates:
            name = validate_glyph_name(str(item["name"]))
            if name not in updated.glyphs:
                raise FontMakerError("GLYPH_NOT_FOUND", f"Unknown glyph: {name}")
            current = updated.glyphs[name].model_dump(mode="json")
            for field in ("advance_width", "left_side_bearing", "right_side_bearing"):
                if field in item:
                    current[field] = item[field]
            updated.glyphs[name] = GlyphRecord.model_validate(current)
            changed.append(f"glyph_metrics:{name}")
        revision = store.save(updated, expected_revision)
        return MutationResult(
            project_id=project_id,
            revision=revision,
            changed=changed,
            suggested_previews=["HHIHH", "HOOH", "nninn", "noon"],
        )

    def set_kerning(
        self,
        project_id: str,
        expected_revision: str,
        *,
        groups: dict[str, list[str]] | None = None,
        upsert_pairs: list[KerningPair] | None = None,
        remove_pairs: list[tuple[str, str]] | None = None,
        remove_groups: list[str] | None = None,
    ) -> MutationResult:
        requested_count = (
            sum(len(members) for members in (groups or {}).values())
            + len(upsert_pairs or [])
            + len(remove_pairs or [])
            + len(remove_groups or [])
        )
        if requested_count > MAX_BATCH_ITEMS:
            raise FontMakerError(
                "INVALID_BATCH_SIZE",
                f"Kerning mutations accept at most {MAX_BATCH_ITEMS} members and rules.",
            )
        store, project = self._store_project(project_id)
        updated = project.model_copy(deep=True)
        for name, members in (groups or {}).items():
            if name.startswith("@"):
                raise FontMakerError("INVALID_KERNING_GROUP", "Group names omit the @ prefix")
            try:
                validate_glyph_name(name)
            except ValueError as exc:
                raise FontMakerError("INVALID_KERNING_GROUP", str(exc)) from exc
            if not members:
                raise FontMakerError("INVALID_KERNING_GROUP", "Kerning groups cannot be empty")
            missing = sorted(set(members) - updated.glyphs.keys())
            if missing:
                raise FontMakerError(
                    "KERNING_GLYPH_NOT_FOUND", f"Unknown group member(s): {', '.join(missing)}"
                )
            updated.kerning.groups[name] = list(dict.fromkeys(members))
        removed_groups = set(remove_groups or [])
        for name in removed_groups:
            updated.kerning.groups.pop(name, None)
        removed = set(remove_pairs or [])
        pairs = {
            (pair.left, pair.right): pair
            for pair in updated.kerning.pairs
            if (pair.left, pair.right) not in removed
            and not (pair.left.startswith("@") and pair.left[1:] in removed_groups)
            and not (pair.right.startswith("@") and pair.right[1:] in removed_groups)
        }
        for pair in upsert_pairs or []:
            self._validate_kern_selector(updated, pair.left)
            self._validate_kern_selector(updated, pair.right)
            pairs[(pair.left, pair.right)] = pair
        updated.kerning.pairs = list(pairs.values())
        revision = store.save(updated, expected_revision)
        return MutationResult(
            project_id=project_id,
            revision=revision,
            changed=["kerning"],
            suggested_previews=["AVATAR", "To Ta Te", "WAY OVER"],
        )

    @staticmethod
    def _validate_kern_selector(project: FontProject, selector: str) -> None:
        if selector.startswith("@"):
            if selector[1:] not in project.kerning.groups:
                raise FontMakerError("KERNING_GROUP_NOT_FOUND", f"Unknown group: {selector}")
        elif selector not in project.glyphs:
            raise FontMakerError("KERNING_GLYPH_NOT_FOUND", f"Unknown glyph: {selector}")

    def set_ligatures(
        self,
        project_id: str,
        expected_revision: str,
        upsert: list[LigatureRule],
        remove: list[dict[str, Any]] | None = None,
    ) -> MutationResult:
        if len(upsert) + len(remove or []) > MAX_BATCH_ITEMS:
            raise FontMakerError(
                "INVALID_BATCH_SIZE",
                f"Ligature mutations accept at most {MAX_BATCH_ITEMS} rules.",
            )
        store, project = self._store_project(project_id)
        updated = project.model_copy(deep=True)
        for rule in upsert:
            missing = sorted(set((*rule.sequence, rule.replacement)) - updated.glyphs.keys())
            if missing:
                raise FontMakerError(
                    "LIGATURE_GLYPH_NOT_FOUND", f"Unknown ligature glyph(s): {', '.join(missing)}"
                )
        removed = {
            (str(item["feature"]), tuple(str(value) for value in item["sequence"]))
            for item in (remove or [])
        }
        rules = {
            (rule.feature, tuple(rule.sequence)): rule
            for rule in updated.ligatures
            if (rule.feature, tuple(rule.sequence)) not in removed
        }
        for rule in upsert:
            rules[(rule.feature, tuple(rule.sequence))] = rule
        updated.ligatures = list(rules.values())
        revision = store.save(updated, expected_revision)
        return MutationResult(
            project_id=project_id,
            revision=revision,
            changed=["ligatures"],
            suggested_previews=["affine office", "fifty difficult", "fi fl ffi ffl"],
        )

    def _glyph_bounds(
        self, store: ProjectStore, project: FontProject, name: str
    ) -> tuple[float, float, float, float]:
        pen = BoundsPen(None)
        for recording in font_space_recordings(
            store.resolve_confined(project.glyphs[name].source, must_exist=True), project.svg
        ):
            recording.replay(pen)
        if pen.bounds is None:
            raise FontMakerError("EMPTY_GLYPH", f"Glyph {name} contains no outline")
        x_min, y_min, x_max, y_max = pen.bounds
        return float(x_min), float(y_min), float(x_max), float(y_max)

    @staticmethod
    def _effective_bearings(
        project: FontProject,
        name: str,
        bounds: tuple[float, float, float, float],
    ) -> tuple[int, int]:
        record = project.glyphs[name]
        x_min, _, x_max, _ = bounds
        outline_width = round(x_max - x_min)
        if record.left_side_bearing is not None:
            left = record.left_side_bearing
        elif record.right_side_bearing is not None:
            left = record.advance_width - outline_width - record.right_side_bearing
        else:
            left = round(x_min)
        return left, record.advance_width - outline_width - left

    def suggest_spacing(
        self,
        project_id: str,
        *,
        glyph_names: list[str] | None = None,
        pair_candidates: list[tuple[str, str]] | None = None,
        target_separation: int | None = None,
    ) -> SpacingProposal:
        store, project = self._store_project(project_id)
        revision = store.revision(project)
        diagnostics: list[Diagnostic] = []
        selected = glyph_names or sorted(name for name in project.glyphs if name != "space")
        for name in selected:
            if name not in project.glyphs:
                raise FontMakerError("GLYPH_NOT_FOUND", f"Unknown glyph: {name}")
        measurement_names = set(selected)
        if target_separation is None:
            controls = {"H", "O", "n", "o"}
            missing_controls = sorted(controls - project.glyphs.keys())
            if missing_controls:
                raise FontMakerError(
                    "SPACING_TARGET_REQUIRED",
                    "Supply target_separation when the complete H/O/n/o control set is unavailable.",
                    missing_controls=missing_controls,
                )
            measurement_names.update(controls)
        bounds = {
            name: self._glyph_bounds(store, project, name) for name in sorted(measurement_names)
        }
        if target_separation is None:
            control_gaps: list[float] = []
            for left, right in (
                ("H", "H"),
                ("H", "O"),
                ("O", "H"),
                ("O", "O"),
                ("n", "n"),
                ("n", "o"),
                ("o", "n"),
                ("o", "o"),
            ):
                if left in bounds and right in bounds:
                    _, left_rsb = self._effective_bearings(project, left, bounds[left])
                    right_lsb, _ = self._effective_bearings(project, right, bounds[right])
                    control_gaps.append(left_rsb + right_lsb)
            target_separation = round(statistics.median(control_gaps))
        target_separation = max(0, min(target_separation, project.metrics.units_per_em))
        candidates = pair_candidates or [
            (text[0], text[1:])
            for text in DEFAULT_RISK_PAIRS
            if text[0] in project.glyphs and text[1:] in project.glyphs
        ]
        for left, right in candidates:
            if left not in project.glyphs or right not in project.glyphs:
                raise FontMakerError(
                    "KERNING_GLYPH_NOT_FOUND", f"Unknown pair candidate: {left}/{right}"
                )

        suggestion = suggest_spacing_with_fontforge(
            store,
            project,
            selected,
            candidates,
            target_separation,
        )
        diagnostics.append(
            Diagnostic(
                code="FONTFORGE_SPACING_HEURISTIC",
                severity=Severity.INFO,
                message="Proposal was measured on a disposable FontForge clone and did not mutate the project.",
                measurements={"fontforge_version": suggestion["fontforge_version"]},
                suggested_action="Review every delta in compiled specimen text before applying it.",
            )
        )

        changes: list[SpacingChange] = []
        for name in selected:
            before_lsb, before_rsb = self._effective_bearings(project, name, bounds[name])
            record = project.glyphs[name]
            after = dict(suggestion["glyph_metrics"][name])
            # FontForge rounds its compiled extrema independently. The durable
            # metrics must use the source-outline width used by validation.
            x_min, _, x_max, _ = bounds[name]
            measured_advance = after["advance_width"]
            after["advance_width"] = (
                round(x_max - x_min)
                + after["left_side_bearing"]
                + after["right_side_bearing"]
            )
            evidence = [
                f"FontForge autoWidth targeted {target_separation} font units of optical separation."
            ]
            if after["advance_width"] != measured_advance:
                evidence.append(
                    f"Reconciled compiled advance {measured_advance} to source-outline advance "
                    f"{after['advance_width']} while preserving the proposed sidebearings."
                )
            before = {
                "advance_width": record.advance_width,
                "left_side_bearing": before_lsb,
                "right_side_bearing": before_rsb,
            }
            if before != after:
                changes.append(
                    SpacingChange(
                        kind="glyph_metrics",
                        glyph=name,
                        before=before,
                        after=after,
                        evidence=evidence,
                    )
                )

        existing = {(pair.left, pair.right): pair.value for pair in project.kerning.pairs}
        for item in suggestion["kerning_pairs"]:
            left = str(item["left"])
            right = str(item["right"])
            value = int(item["value"])
            if value != existing.get((left, right), 0):
                changes.append(
                    SpacingChange(
                        kind="kerning",
                        left=left,
                        right=right,
                        before={"value": existing.get((left, right), 0)},
                        after={"value": value},
                        evidence=[
                            f"FontForge autoKern targeted {target_separation} font units of optical separation."
                        ],
                    )
                )
        proposal = SpacingProposal(
            proposal_id=str(uuid.uuid4()),
            project_id=project_id,
            base_revision=revision,
            target_separation=target_separation,
            changes=changes,
            preview_strings=["HHIHH HOOH", "nninn noon", "AVATAR To Ta Te", "WAY OVER"],
            diagnostics=diagnostics,
        )
        ProjectCache(store.state_dir).put_proposal(
            proposal.proposal_id, revision, proposal.model_dump(mode="json")
        )
        return proposal

    def apply_spacing_proposal(
        self, project_id: str, expected_revision: str, proposal_id: str
    ) -> MutationResult:
        store, project = self._store_project(project_id)
        raw = ProjectCache(store.state_dir).get_proposal(proposal_id)
        if raw is None:
            raise FontMakerError("PROPOSAL_NOT_FOUND", f"Unknown proposal: {proposal_id}")
        proposal = SpacingProposal.model_validate(raw)
        if proposal.project_id != project_id:
            raise FontMakerError("PROPOSAL_PROJECT_MISMATCH", "Proposal belongs to another project")
        current_revision = store.revision(project)
        if expected_revision != current_revision or proposal.base_revision != current_revision:
            raise RevisionConflict(proposal.base_revision, current_revision)
        updated = project.model_copy(deep=True)
        pairs = {(pair.left, pair.right): pair for pair in updated.kerning.pairs}
        changed = []
        for change in proposal.changes:
            if change.kind == "glyph_metrics" and change.glyph:
                record = updated.glyphs[change.glyph]
                record.advance_width = change.after["advance_width"]
                record.left_side_bearing = change.after["left_side_bearing"]
                record.right_side_bearing = change.after["right_side_bearing"]
                changed.append(f"glyph_metrics:{change.glyph}")
            elif change.kind == "kerning" and change.left and change.right:
                pair = KerningPair(
                    left=change.left, right=change.right, value=change.after["value"]
                )
                pairs[(change.left, change.right)] = pair
                changed.append(f"kerning:{change.left}/{change.right}")
        updated.kerning.pairs = list(pairs.values())
        revision = store.save(updated, expected_revision)
        return MutationResult(
            project_id=project_id,
            revision=revision,
            changed=changed,
            suggested_previews=proposal.preview_strings,
        )

    def validate(self, project_id: str, *, temporary_build: bool = False) -> list[Diagnostic]:
        store, project = self._store_project(project_id)
        diagnostics: list[Diagnostic] = []
        portable_sources: dict[str, str] = {}
        for name, glyph in project.glyphs.items():
            key = glyph.source.casefold()
            if previous := portable_sources.get(key):
                diagnostics.append(
                    Diagnostic(
                        code="GLYPH_SOURCE_PATH_COLLISION",
                        severity=Severity.ERROR,
                        message=(
                            f"Glyphs {previous} and {name} use source paths that collide on "
                            "case-insensitive filesystems. Reimport both glyphs."
                        ),
                        glyph=name,
                    )
                )
            else:
                portable_sources[key] = name
        for name, glyph in project.glyphs.items():
            path = store.resolve_confined(glyph.source)
            if not path.is_file():
                diagnostics.append(
                    Diagnostic(
                        code="MISSING_GLYPH_SOURCE",
                        severity=Severity.ERROR,
                        message=f"Missing source: {glyph.source}",
                        glyph=name,
                    )
                )
                continue
            try:
                normalized = normalize_svg(path, project.svg)
                if normalized.bounds is not None:
                    _, y_min, _, y_max = normalized.bounds
                    if (
                        y_min < project.svg.view_box[1]
                        or y_max > project.svg.view_box[1] + project.svg.view_box[3]
                    ):
                        diagnostics.append(
                            Diagnostic(
                                code="GLYPH_OUTSIDE_VIEWBOX",
                                severity=Severity.WARNING,
                                message="Outline extends outside the shared SVG viewBox.",
                                glyph=name,
                                measurements={"svg_y_min": y_min, "svg_y_max": y_max},
                            )
                        )
            except FontMakerError as exc:
                diagnostics.append(
                    Diagnostic(
                        code=exc.code, severity=Severity.ERROR, message=exc.message, glyph=name
                    )
                )
            if glyph.advance_width == 0 and name != ".notdef":
                diagnostics.append(
                    Diagnostic(
                        code="ZERO_ADVANCE",
                        severity=Severity.WARNING,
                        message="Glyph has zero advance width.",
                        glyph=name,
                    )
                )
            if glyph.left_side_bearing is not None and glyph.right_side_bearing is not None:
                try:
                    bounds = self._glyph_bounds(store, project, name)
                except FontMakerError:
                    continue
                expected_advance = (
                    round(bounds[2] - bounds[0])
                    + glyph.left_side_bearing
                    + glyph.right_side_bearing
                )
                if glyph.advance_width != expected_advance:
                    diagnostics.append(
                        Diagnostic(
                            code="INCONSISTENT_GLYPH_METRICS",
                            severity=Severity.ERROR,
                            message=(
                                "Advance width does not equal outline width plus the explicit "
                                "left and right sidebearings."
                            ),
                            glyph=name,
                            measurements={
                                "advance_width": glyph.advance_width,
                                "expected_advance_width": expected_advance,
                            },
                            suggested_action=(
                                "Change the advance or clear one sidebearing so the remaining "
                                "value determines outline placement."
                            ),
                        )
                    )
        for group, members in project.kerning.groups.items():
            try:
                validate_glyph_name(group)
            except ValueError:
                diagnostics.append(
                    Diagnostic(
                        code="INVALID_KERNING_GROUP",
                        severity=Severity.ERROR,
                        message="Kerning group name is not a safe identifier.",
                        rule=f"@{group}",
                    )
                )
            if not members:
                diagnostics.append(
                    Diagnostic(
                        code="EMPTY_KERNING_GROUP",
                        severity=Severity.ERROR,
                        message="Kerning groups must contain at least one glyph.",
                        rule=f"@{group}",
                    )
                )
            missing = sorted(set(members) - project.glyphs.keys())
            if missing:
                diagnostics.append(
                    Diagnostic(
                        code="KERNING_GLYPH_NOT_FOUND",
                        severity=Severity.ERROR,
                        message=f"Missing group member(s): {', '.join(missing)}",
                        rule=f"@{group}",
                    )
                )
        for pair in project.kerning.pairs:
            for selector in (pair.left, pair.right):
                try:
                    self._validate_kern_selector(project, selector)
                except FontMakerError as exc:
                    diagnostics.append(
                        Diagnostic(
                            code=exc.code,
                            severity=Severity.ERROR,
                            message=exc.message,
                            rule=f"{pair.left}/{pair.right}",
                        )
                    )
        for rule in project.ligatures:
            missing_ligature_glyphs = (
                set((*rule.sequence, rule.replacement)) - project.glyphs.keys()
            )
            if missing_ligature_glyphs:
                diagnostics.append(
                    Diagnostic(
                        code="LIGATURE_GLYPH_NOT_FOUND",
                        severity=Severity.ERROR,
                        message=(f"Missing glyph(s): {', '.join(sorted(missing_ligature_glyphs))}"),
                        rule=f"{rule.feature}:{'+'.join(rule.sequence)}",
                    )
                )
        if not project.font.license_text:
            diagnostics.append(
                Diagnostic(
                    code="FONT_LICENSE_UNSET",
                    severity=Severity.INFO,
                    message="The generated font has no user-selected license metadata.",
                )
            )
        if temporary_build and not any(item.severity == Severity.ERROR for item in diagnostics):
            try:
                _, build_diagnostics, _ = build_font(store, project, ["ttf"], persist=False)
                diagnostics.extend(build_diagnostics)
            except FontMakerError as exc:
                diagnostics.append(
                    Diagnostic(code=exc.code, severity=Severity.ERROR, message=exc.message)
                )
        return diagnostics

    def build(self, project_id: str, formats: list[str] | None = None) -> dict[str, Any]:
        store, project = self._store_project(project_id)
        diagnostics = self.validate(project_id)
        errors = [item for item in diagnostics if item.severity == Severity.ERROR]
        if errors:
            raise FontMakerError(
                "VALIDATION_FAILED",
                "Font has validation errors and was not built.",
                diagnostics=[item.model_dump(mode="json") for item in errors],
            )
        artifacts, build_diagnostics, metadata = build_font(store, project, formats)
        cache = ProjectCache(store.state_dir)
        for artifact in artifacts:
            cache.put_artifact(
                artifact.artifact_id, artifact.revision, artifact.model_dump(mode="json")
            )
        return {
            "project_id": project_id,
            "revision": store.revision(project),
            "artifacts": [item.model_dump(mode="json") for item in artifacts],
            "diagnostics": [
                item.model_dump(mode="json") for item in diagnostics + build_diagnostics
            ],
            "backend": metadata,
        }

    def shape(
        self, project_id: str, text: str, features: dict[str, bool] | None = None
    ) -> dict[str, Any]:
        if not text or len(text) > MAX_PREVIEW_TEXT_LENGTH:
            raise FontMakerError(
                "INVALID_TEXT_LENGTH",
                f"Shaping text must contain 1 to {MAX_PREVIEW_TEXT_LENGTH} characters.",
            )
        built = self.build(project_id, ["ttf"])
        store, _ = self._store_project(project_id)
        font_artifact = built["artifacts"][0]
        shaping = shape_font(
            store.resolve_confined(font_artifact["path"], must_exist=True), text, features
        )
        return {**shaping, "project_id": project_id, "revision": built["revision"]}

    def preview(
        self,
        project_id: str,
        text: str,
        features: dict[str, bool] | None = None,
        *,
        font_size: int = 96,
        pixel_scale: int = 3,
        guides: bool = True,
    ) -> tuple[dict[str, Any], bytes]:
        if not text or len(text) > MAX_PREVIEW_TEXT_LENGTH:
            raise FontMakerError(
                "INVALID_TEXT_LENGTH",
                f"Preview text must contain 1 to {MAX_PREVIEW_TEXT_LENGTH} characters.",
            )
        if not 8 <= font_size <= 512:
            raise FontMakerError("INVALID_FONT_SIZE", "Preview font size must be from 8 to 512.")
        if not 1 <= pixel_scale <= 4:
            raise FontMakerError("INVALID_PIXEL_SCALE", "Preview pixel scale must be from 1 to 4.")
        built = self.build(project_id, ["ttf"])
        store, project = self._store_project(project_id)
        font_path = store.resolve_confined(built["artifacts"][0]["path"], must_exist=True)
        artifacts, shaping, png = write_preview(
            store,
            project,
            font_path,
            text,
            features,
            font_size=font_size,
            pixel_scale=pixel_scale,
            guides=guides,
        )
        cache = ProjectCache(store.state_dir)
        for artifact in artifacts:
            cache.put_artifact(
                artifact.artifact_id, artifact.revision, artifact.model_dump(mode="json")
            )
        return (
            {
                "project_id": project_id,
                "revision": store.revision(project),
                "settings": {
                    "text": text,
                    "features": features or {"kern": True, "liga": True},
                    "font_size": font_size,
                    "pixel_scale": pixel_scale,
                    "guides": guides,
                },
                "artifacts": [item.model_dump(mode="json") for item in artifacts],
                "shaping": shaping,
            },
            png,
        )

    def doctor(self) -> dict[str, Any]:
        executable = find_fontforge()
        version = fontforge_version(executable)
        return {
            "font_maker_version": "0.1.0",
            "fontforge": {
                "available": executable is not None,
                "executable": executable,
                "version": version,
                "required_version": SUPPORTED_FONTFORGE_VERSION,
                "compatible": version == SUPPORTED_FONTFORGE_VERSION,
                "license": "GPL-3.0-or-later",
                "credit": "FontForge by George Williams and the FontForge contributors",
                "source": "https://github.com/fontforge/fontforge/tree/20251009",
            },
            "formats": ["ttf", "otf", "woff2"],
            "transport": "stdio",
        }
