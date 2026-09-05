"""Semantic version value object for prompt assets."""

from __future__ import annotations


class PromptVersion:
    """SemVer (major.minor.patch) with optional pre-release and build metadata."""
    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        pre_release: str | None = None,
        build_metadata: str | None = None,
    ) -> None:
        if major < 0:
            raise ValueError("Major version must be non-negative.")
        if minor < 0:
            raise ValueError("Minor version must be non-negative.")
        if patch < 0:
            raise ValueError("Patch version must be non-negative.")
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre_release = (
            pre_release.strip() if pre_release and pre_release.strip() else None
        )
        self.build_metadata = (
            build_metadata.strip()
            if build_metadata and build_metadata.strip()
            else None
        )

    @property
    def is_pre_release(self) -> bool:
        """True when a pre-release label is set."""
        return bool(self.pre_release)

    @property
    def is_stable(self) -> bool:
        """True when there is no pre-release label."""
        return not self.is_pre_release

    @classmethod
    def create(
        cls,
        major: int,
        minor: int = 0,
        patch: int = 0,
        pre_release: str | None = None,
        build_metadata: str | None = None,
    ) -> PromptVersion:
        """Build a version; omitted minor/patch default to 0."""
        return cls(major, minor, patch, pre_release, build_metadata)

    @classmethod
    def initial(cls) -> PromptVersion:
        """``1.0.0``."""
        return cls(1, 0, 0)

    @classmethod
    def parse(cls, version: str) -> PromptVersion:
        """Parse ``MAJOR``, ``MAJOR.MINOR``, or ``MAJOR.MINOR.PATCH`` with optional ``-pre`` and ``+build``."""
        if version is None or not str(version).strip():
            raise ValueError("Version string cannot be null or empty.")
        original = version
        text = version.strip()
        build_metadata = None
        pre_release = None
        plus = text.find("+")
        if plus >= 0:
            build_metadata = text[plus + 1 :]
            text = text[:plus]
        dash = text.find("-")
        if dash >= 0:
            pre_release = text[dash + 1 :]
            text = text[:dash]
        parts = text.split(".")
        if len(parts) < 1 or len(parts) > 3:
            raise ValueError(
                f"Invalid version format: '{original}'. Expected MAJOR.MINOR.PATCH."
            )
        try:
            major = int(parts[0])
        except ValueError as exc:
            raise ValueError(f"Invalid major version in '{original}'.") from exc
        if len(parts) > 1 and not parts[1].isdigit():
            raise ValueError(f"Invalid minor version in '{original}'.")
        if len(parts) > 2 and not parts[2].isdigit():
            raise ValueError(f"Invalid patch version in '{original}'.")
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return cls(major, minor, patch, pre_release, build_metadata)

    @classmethod
    def try_parse(cls, version: str | None) -> PromptVersion | None:
        """Like ``parse``, but returns ``None`` instead of raising."""
        if version is None or not str(version).strip():
            return None
        try:
            return cls.parse(version)
        except (ValueError, TypeError):
            return None

    def next_major(self) -> PromptVersion:
        """``(major+1).0.0`` with pre-release and build cleared."""
        return PromptVersion(self.major + 1, 0, 0)

    def next_minor(self) -> PromptVersion:
        """``major.(minor+1).0``."""
        return PromptVersion(self.major, self.minor + 1, 0)

    def next_patch(self) -> PromptVersion:
        """Increment patch only."""
        return PromptVersion(self.major, self.minor, self.patch + 1)

    def with_pre_release(self, label: str) -> PromptVersion:
        """Copy with a new pre-release label."""
        return PromptVersion(
            self.major, self.minor, self.patch, label, self.build_metadata
        )

    def with_build_metadata(self, metadata: str) -> PromptVersion:
        """Copy with new ``+build`` metadata."""
        return PromptVersion(
            self.major, self.minor, self.patch, self.pre_release, metadata
        )

    def to_stable(self) -> PromptVersion:
        """Same numbers with pre-release and build stripped."""
        return PromptVersion(self.major, self.minor, self.patch)

    def is_compatible_with(self, other: PromptVersion | None) -> bool:
        """True if this version is the same major and at least as high as ``other``."""
        if other is None:
            return False
        return self.major == other.major and (
            self.minor > other.minor
            or (self.minor == other.minor and self.patch >= other.patch)
        )

    def __lt__(self, other: PromptVersion) -> bool:
        return self._cmp(other) < 0

    def __le__(self, other: PromptVersion) -> bool:
        return self._cmp(other) <= 0

    def __gt__(self, other: PromptVersion) -> bool:
        return self._cmp(other) > 0

    def __ge__(self, other: PromptVersion) -> bool:
        return self._cmp(other) >= 0

    def _cmp(self, other: PromptVersion | None) -> int:
        if other is None:
            return 1
        if self.major != other.major:
            return self.major - other.major
        if self.minor != other.minor:
            return self.minor - other.minor
        if self.patch != other.patch:
            return self.patch - other.patch
        if self.is_pre_release and not other.is_pre_release:
            return -1
        if not self.is_pre_release and other.is_pre_release:
            return 1
        if self.is_pre_release and other.is_pre_release:
            a = self.pre_release or ""
            b = other.pre_release or ""
            if a < b:
                return -1
            if a > b:
                return 1
        return 0

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PromptVersion)
            and self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
        )

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.pre_release))

    def __str__(self) -> str:
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            result += f"-{self.pre_release}"
        if self.build_metadata:
            result += f"+{self.build_metadata}"
        return result

    def __repr__(self) -> str:
        return f"PromptVersion({self})"
