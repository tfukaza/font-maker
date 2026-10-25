from __future__ import annotations

import re

import pytest

from font_maker.errors import RevisionConflict
from font_maker.models import VerticalMetrics
from font_maker.store import ProjectStore


def test_create_project_writes_manifest_and_single_baseline(tmp_path):
    store, project = ProjectStore.create(tmp_path / "test-font", "Test Font")

    assert project.metrics == VerticalMetrics()
    assert store.manifest_path.is_file()
    template = (store.root / "glyph-template.svg").read_text(encoding="utf-8")
    assert len(re.findall(r'data-fontmaker-baseline="true"', template)) == 1
    assert '<g id="glyph"' in template


def test_revision_is_stable_and_conflicts_are_detected(tmp_path):
    store, project = ProjectStore.create(tmp_path / "test-font", "Test Font")
    first = store.revision(project)
    assert first == store.revision(store.load())

    updated = project.model_copy(deep=True)
    updated.font.style_name = "Bold"
    store.save(updated, first)

    with pytest.raises(RevisionConflict) as conflict:
        store.save(project, first)
    assert conflict.value.details["current_revision"] != first
    assert conflict.value.details["changed_sections"]


@pytest.mark.parametrize("update_metrics", [False, True])
def test_deep_descender_guide_fits_shared_canvas(tmp_path, update_metrics):
    from xml.etree import ElementTree

    from font_maker.service import FontMakerService

    metrics = VerticalMetrics(ascender=800, descender=-270)
    service = FontMakerService()
    created = service.create_project(
        str(tmp_path / "deep-font"), "Deep Font", metrics=None if update_metrics else metrics
    )
    if update_metrics:
        service.set_font_metrics(created["project_id"], created["revision"], metrics)
    store = ProjectStore(tmp_path / "deep-font")
    project = store.load()
    assert project.svg.scale == 1
    assert project.svg.baseline_y == 800
    template = ElementTree.parse(store.root / "glyph-template.svg").getroot()
    _x, y, width, height = map(float, template.attrib["viewBox"].split())
    assert width == 1000
    for guide in template.findall(".//{http://www.w3.org/2000/svg}line"):
        assert y <= float(guide.attrib["y1"]) <= y + height


def test_confined_paths_reject_escape(tmp_path):
    store, _ = ProjectStore.create(tmp_path / "test-font", "Test Font")
    with pytest.raises(Exception, match="escapes"):
        store.resolve_confined("../outside.svg")
