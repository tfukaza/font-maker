from font_maker.design_session import DesignSessionStore, FontBrief, FontConcept, build_agent_prompt


def test_guided_brief_becomes_ready() -> None:
    store = DesignSessionStore()
    session = store.create(sample_text="Signal Lost", mode="guided")
    brief = FontBrief(
        mode="guided",
        sample_text="Signal Lost",
        purpose="science-fiction game title",
        construction="pixel",
        personalities=["sci-fi", "ominous"],
        serif_style="sans",
        weight="bold",
        width="wide",
        corners="sharp",
        contrast="even",
    )

    updated = store.update(session.session_id, brief)
    final = store.finalize(session.session_id)

    assert updated.missing_fields == []
    assert final.status == "ready"
    assert '"Signal Lost"' in final.prompt
    assert "pixel construction" in final.prompt
    assert "science-fiction game title" in final.prompt


def test_describe_mode_requires_description() -> None:
    store = DesignSessionStore()
    session = store.create(mode="describe")

    assert session.missing_fields == ["font description"]


def test_concepts_replace_the_current_agent_directions() -> None:
    store = DesignSessionStore()
    session = store.create(mode="explore")
    concept = FontConcept(
        concept_id="signal-grid",
        title="Signal Grid",
        description="Wide modular forms with clipped terminals.",
    )

    updated = store.submit_concepts(session.session_id, [concept])

    assert updated.concepts == [concept]


def test_prompt_omits_empty_optional_sentences() -> None:
    prompt = build_agent_prompt(FontBrief(mode="guided", sample_text="Type"))

    assert "Intended use:" not in prompt
    assert "Practical constraints:" not in prompt
    assert "exactly the sample text" in prompt
