"""In-memory state and prompt assembly for the font design interview."""

from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

DesignMode = Literal["describe", "explore", "guided"]


class FontBrief(BaseModel):
    """The user-facing choices translated into a stable agent brief."""

    mode: DesignMode | None = None
    sample_text: str = "Hamburgefontsiv"
    purpose: str = ""
    languages: list[str] = Field(default_factory=lambda: ["Latin"])
    description: str = ""
    construction: Literal["smooth", "pixel", "textured"] | None = None
    personalities: list[str] = Field(default_factory=list)
    serif_style: Literal["sans", "serif", "slab"] | None = None
    weight: Literal["light", "regular", "bold"] | None = None
    width: Literal["narrow", "regular", "wide"] | None = None
    corners: Literal["sharp", "soft", "round"] | None = None
    contrast: Literal["even", "moderate", "dramatic"] | None = None
    regularity: Literal["precise", "human", "expressive"] | None = None
    slant: Literal["upright", "slight", "italic"] | None = None
    decoration: Literal["minimal", "distinctive", "ornate"] | None = None
    constraints: str = ""


class FontConcept(BaseModel):
    """A visual direction submitted by the agent for display in the app."""

    concept_id: str
    title: str
    description: str
    image_uri: str | None = None


class DesignSession(BaseModel):
    """A recoverable snapshot exchanged between the MCP App and the agent."""

    session_id: str
    created_at: str
    updated_at: str
    status: Literal["draft", "ready"] = "draft"
    brief: FontBrief
    concepts: list[FontConcept] = Field(default_factory=list)
    prompt: str
    missing_fields: list[str]
    completion: float


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def missing_fields(brief: FontBrief) -> list[str]:
    """Return the small set of choices needed for a useful first generation."""

    missing: list[str] = []
    if brief.mode is None:
        missing.append("design route")
    if not _clean(brief.sample_text):
        missing.append("sample text")
    if brief.mode == "describe" and not _clean(brief.description):
        missing.append("font description")
    if brief.mode in {"explore", "guided"}:
        if brief.construction is None:
            missing.append("edge style")
        if not brief.personalities:
            missing.append("personality")
    if brief.mode == "guided":
        if brief.serif_style is None:
            missing.append("stroke endings")
        if brief.weight is None:
            missing.append("weight")
    return missing


def build_agent_prompt(brief: FontBrief) -> str:
    """Translate plain-language choices into an explicit font-generation prompt."""

    lines = [
        "Design a new static, monochrome typeface from the following creative brief.",
        f'Sample text for concept specimens: "{_clean(brief.sample_text) or "Hamburgefontsiv"}".',
    ]

    if _clean(brief.purpose):
        lines.append(f"Intended use: {_clean(brief.purpose)}.")
    if brief.languages:
        lines.append(f"Required writing systems or languages: {', '.join(brief.languages)}.")
    if _clean(brief.description):
        lines.append(f"User description: {_clean(brief.description)}")

    traits: list[str] = []
    if brief.construction:
        traits.append(f"{brief.construction} construction")
    if brief.personalities:
        traits.append(" / ".join(brief.personalities) + " personality")
    if brief.serif_style:
        traits.append(f"{brief.serif_style} stroke endings")
    if brief.weight:
        traits.append(f"{brief.weight} weight")
    if brief.width:
        traits.append(f"{brief.width} width")
    if brief.corners:
        traits.append(f"{brief.corners} corners")
    if brief.contrast:
        traits.append(f"{brief.contrast} thick-thin contrast")
    if brief.regularity:
        traits.append(f"{brief.regularity} shape regularity")
    if brief.slant:
        traits.append(f"{brief.slant} slant")
    if brief.decoration:
        traits.append(f"{brief.decoration} decoration")
    if traits:
        lines.append("Visual direction: " + "; ".join(traits) + ".")

    if _clean(brief.constraints):
        lines.append(f"Practical constraints: {_clean(brief.constraints)}")

    lines.extend(
        [
            "Begin with three clearly different concept specimens using exactly the sample text.",
            "Keep the words, scale, color, and presentation consistent so the "
            "letterforms can be compared fairly.",
            "After a direction is selected, establish shared font metrics and draw "
            "import-ready SVG glyph outlines.",
        ]
    )
    return "\n".join(lines)


def _snapshot(
    session_id: str,
    created_at: str,
    updated_at: str,
    brief: FontBrief,
    concepts: list[FontConcept],
    status: Literal["draft", "ready"] = "draft",
) -> DesignSession:
    missing = missing_fields(brief)
    required_count = len(missing) + 1
    completion = 1.0 if not missing else round(1 / required_count, 2)
    return DesignSession(
        session_id=session_id,
        created_at=created_at,
        updated_at=updated_at,
        status=status,
        brief=brief,
        concepts=concepts,
        prompt=build_agent_prompt(brief),
        missing_fields=missing,
        completion=completion,
    )


class DesignSessionStore:
    """Thread-safe process-local storage for short-lived design interviews."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._sessions: dict[str, DesignSession] = {}

    def create(
        self,
        *,
        sample_text: str = "Hamburgefontsiv",
        starting_description: str = "",
        mode: DesignMode | None = None,
    ) -> DesignSession:
        now = datetime.now(UTC).isoformat()
        brief = FontBrief(
            mode=mode,
            sample_text=sample_text,
            description=starting_description,
        )
        session = _snapshot(uuid4().hex, now, now, brief, [])
        with self._lock:
            self._sessions[session.session_id] = session
        return session.model_copy(deep=True)

    def get(self, session_id: str) -> DesignSession:
        with self._lock:
            try:
                session = self._sessions[session_id]
            except KeyError as exc:
                raise ValueError(f"Unknown font design session: {session_id}") from exc
            return session.model_copy(deep=True)

    def update(self, session_id: str, brief: FontBrief) -> DesignSession:
        with self._lock:
            current = self.get(session_id)
            updated = _snapshot(
                session_id,
                current.created_at,
                datetime.now(UTC).isoformat(),
                brief,
                current.concepts,
                current.status,
            )
            self._sessions[session_id] = updated
            return updated.model_copy(deep=True)

    def submit_concepts(self, session_id: str, concepts: list[FontConcept]) -> DesignSession:
        with self._lock:
            current = self.get(session_id)
            updated = _snapshot(
                session_id,
                current.created_at,
                datetime.now(UTC).isoformat(),
                current.brief,
                concepts,
                current.status,
            )
            self._sessions[session_id] = updated
            return updated.model_copy(deep=True)

    def finalize(self, session_id: str) -> DesignSession:
        with self._lock:
            current = self.get(session_id)
            if current.missing_fields:
                missing = ", ".join(current.missing_fields)
                raise ValueError(f"The font brief still needs: {missing}")
            updated = current.model_copy(
                update={
                    "status": "ready",
                    "updated_at": datetime.now(UTC).isoformat(),
                },
                deep=True,
            )
            self._sessions[session_id] = updated
            return updated.model_copy(deep=True)
