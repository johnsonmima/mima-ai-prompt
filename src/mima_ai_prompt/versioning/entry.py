"""Associates content and audit information with one prompt version."""

from __future__ import annotations

from typing import Generic, TypeVar

from mima_ai_prompt._utils import utc_now
from mima_ai_prompt.models.version import PromptVersion

T = TypeVar("T")


class VersionEntry(Generic[T]):
    """One history row: version, content, change log, author, timestamp."""

    def __init__(
        self,
        version: PromptVersion,
        content: T,
        change_log: str | None,
        author: str | None,
    ) -> None:
        self.version = version
        self.content = content
        self.change_log = change_log
        self.author = author
        self.timestamp = utc_now()

    def __str__(self) -> str:
        base = f"v{self.version} ({self.timestamp:%Y-%m-%d})"
        if self.change_log:
            return f"{base}: {self.change_log}"
        return base
