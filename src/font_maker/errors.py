"""Stable domain errors shared by the CLI and MCP adapters."""

from __future__ import annotations

from typing import Any


class FontMakerError(Exception):
    """An error safe to expose to an agent or CLI user."""

    def __init__(self, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class RevisionConflict(FontMakerError):
    def __init__(
        self,
        expected: str,
        current: str,
        changed_sections: list[str] | None = None,
    ) -> None:
        super().__init__(
            "REVISION_CONFLICT",
            "The project changed since it was inspected.",
            expected_revision=expected,
            current_revision=current,
            changed_sections=changed_sections or ["manifest_or_referenced_sources"],
        )
