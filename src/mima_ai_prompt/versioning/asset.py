"""Named content with semantic version and lifecycle metadata."""

from __future__ import annotations

from typing import Generic, TypeVar

from mima_ai_prompt._utils import new_id, utc_now
from mima_ai_prompt.models.version import PromptVersion

T = TypeVar("T")


class VersionedPromptAsset(Generic[T]):
    """One named payload at one SemVer, plus author/tags/deprecation."""

    def __init__(
        self,
        name: str,
        version: PromptVersion,
        content: T,
        id: str | None = None,
    ) -> None:
        if not name or not str(name).strip():
            raise ValueError("Asset name cannot be null or empty.")
        if version is None:
            raise TypeError("version cannot be None")
        if content is None:
            raise TypeError("content cannot be None")
        self.id = id or new_id()
        self.name = name
        self.version = version
        self.content = content
        self.description: str | None = None
        self.author: str | None = None
        self.tags: list[str] = []
        self.created_at = utc_now()
        self.change_log: str | None = None
        self.is_deprecated = False
        self.deprecation_message: str | None = None

    @classmethod
    def create(
        cls, name: str, version: PromptVersion, content: T
    ) -> VersionedPromptAsset[T]:
        """Named asset at ``version`` holding ``content``."""
        return cls(name, version, content)

    def with_description(self, description: str) -> VersionedPromptAsset[T]:
        """Set ``description`` on this instance."""
        self.description = description
        return self

    def with_author(self, author: str) -> VersionedPromptAsset[T]:
        """Set ``author`` on this instance."""
        self.author = author
        return self

    def with_tags(self, *tags: str) -> VersionedPromptAsset[T]:
        """Replace tags with the given names."""
        self.tags = list(tags)
        return self

    def with_change_log(self, change_log: str) -> VersionedPromptAsset[T]:
        """Set the change-log note for this version."""
        self.change_log = change_log
        return self

    def deprecate(self, reason: str) -> VersionedPromptAsset[T]:
        """Mark this version deprecated and record ``reason``."""
        self.is_deprecated = True
        self.deprecation_message = reason
        return self

    def _spawn(
        self, version: PromptVersion, new_content: T, change_log: str | None
    ) -> VersionedPromptAsset[T]:
        nxt = VersionedPromptAsset(self.name, version, new_content)
        nxt.description = self.description
        nxt.author = self.author
        nxt.tags = list(self.tags)
        nxt.change_log = change_log
        return nxt

    def bump_major(
        self, new_content: T, change_log: str | None = None
    ) -> VersionedPromptAsset[T]:
        """Return a new asset identity at the next major version."""
        return self._spawn(
            self.version.next_major(), new_content, change_log or "Breaking change"
        )

    def bump_minor(
        self, new_content: T, change_log: str | None = None
    ) -> VersionedPromptAsset[T]:
        """Return a new asset identity at the next minor version."""
        return self._spawn(
            self.version.next_minor(), new_content, change_log or "New feature"
        )

    def bump_patch(
        self, new_content: T, change_log: str | None = None
    ) -> VersionedPromptAsset[T]:
        """Return a new asset identity at the next patch version."""
        return self._spawn(
            self.version.next_patch(), new_content, change_log or "Bug fix"
        )

    def __str__(self) -> str:
        deprecated = " [DEPRECATED]" if self.is_deprecated else ""
        return f"{self.name} v{self.version}{deprecated}"
