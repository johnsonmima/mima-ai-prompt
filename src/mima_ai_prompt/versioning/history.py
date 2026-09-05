"""Indexes and queries all versions of a named prompt asset."""

from __future__ import annotations

from typing import Generic, TypeVar

from mima_ai_prompt.models.version import PromptVersion
from mima_ai_prompt.versioning.entry import VersionEntry

T = TypeVar("T")


class PromptVersionHistory(Generic[T]):
    """In-memory map of SemVer → content for one named asset."""

    def __init__(self, asset_name: str) -> None:
        if not asset_name or not str(asset_name).strip():
            raise ValueError("Asset name cannot be null or empty.")
        self.asset_name = asset_name
        self._versions: dict[PromptVersion, VersionEntry[T]] = {}

    @classmethod
    def create(cls, asset_name: str) -> PromptVersionHistory[T]:
        """Empty history for ``asset_name``."""
        return cls(asset_name)

    @property
    def all(self) -> list[VersionEntry[T]]:
        """All entries sorted by version, lowest first."""
        return sorted(self._versions.values(), key=lambda e: e.version)

    @property
    def count(self) -> int:
        """Number of stored versions."""
        return len(self._versions)

    @property
    def latest(self) -> VersionEntry[T] | None:
        """Highest version, including pre-releases."""
        items = self.all
        return items[-1] if items else None

    @property
    def latest_stable(self) -> VersionEntry[T] | None:
        """Highest version that is not a pre-release."""
        stables = [e for e in self.all if e.version.is_stable]
        return stables[-1] if stables else None

    def add(
        self,
        version: PromptVersion,
        content: T,
        change_log: str | None = None,
        author: str | None = None,
    ) -> PromptVersionHistory[T]:
        """Register a version. Duplicate versions raise."""
        if version is None:
            raise TypeError("version cannot be None")
        if content is None:
            raise TypeError("content cannot be None")
        if version in self._versions:
            raise RuntimeError(
                f"Version {version} already exists in history for '{self.asset_name}'."
            )
        self._versions[version] = VersionEntry(version, content, change_log, author)
        return self

    def get(self, version: PromptVersion) -> VersionEntry[T] | None:
        """Entry for ``version``, or ``None``."""
        return self._versions.get(version)

    def get_content(self, version: PromptVersion) -> T | None:
        """Payload for ``version``, or ``None``."""
        entry = self.get(version)
        return entry.content if entry else None

    def contains(self, version: PromptVersion) -> bool:
        """True if ``version`` is already stored."""
        return version in self._versions

    def get_range(
        self, from_version: PromptVersion, to_version: PromptVersion
    ) -> list[VersionEntry[T]]:
        """Entries whose version is between ``from_version`` and ``to_version`` inclusive."""
        return [e for e in self.all if from_version <= e.version <= to_version]

    def get_change_log(
        self, from_version: PromptVersion, to_version: PromptVersion
    ) -> list[str]:
        """``vX.Y.Z: notes`` lines for entries in range that have a change log."""
        return [
            f"v{e.version}: {e.change_log}"
            for e in self.get_range(from_version, to_version)
            if e.change_log
        ]
