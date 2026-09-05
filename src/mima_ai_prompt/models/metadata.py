"""Name, tags, version, timestamps, and optional provider/model hints on a message or prompt."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from mima_ai_prompt._utils import utc_now
from mima_ai_prompt.models.version import PromptVersion


class MessageMetadata:
    """Copy-on-write bag of labels. ``set_*`` methods return a new instance."""

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        category: str | None = None,
        version: str | None = None,
        author: str | None = None,
        tags: Iterable[str] | None = None,
        language: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        created: datetime | None = None,
        modified: datetime | None = None,
        min_compatible_version: str | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.category = category
        self.version = version
        self.author = author
        self.tags = list(tags) if tags is not None else []
        self.language = language
        self.provider = provider
        self.model = model
        self.created = created or utc_now()
        self.modified = modified or utc_now()
        self.min_compatible_version = min_compatible_version

    @property
    def semantic_version(self) -> PromptVersion | None:
        """``version`` parsed as SemVer, or ``None`` if it is missing or invalid."""
        return PromptVersion.try_parse(self.version)

    @classmethod
    def with_name(cls, name: str) -> MessageMetadata:
        """Metadata whose only set field is ``name``."""
        return cls(name=name)

    @classmethod
    def empty(cls) -> MessageMetadata:
        """All fields empty except ``created`` / ``modified`` timestamps."""
        return cls()

    def _copy(self, **kwargs: object) -> MessageMetadata:
        data = dict(
            name=self.name,
            description=self.description,
            category=self.category,
            version=self.version,
            author=self.author,
            tags=self.tags,
            language=self.language,
            provider=self.provider,
            model=self.model,
            created=self.created,
            modified=utc_now(),
            min_compatible_version=self.min_compatible_version,
        )
        data.update(kwargs)
        return MessageMetadata(**data)  # type: ignore[arg-type]

    def set_name(self, name: str) -> MessageMetadata:
        """Return a copy with ``name`` updated."""
        return self._copy(name=name)

    def set_description(self, description: str) -> MessageMetadata:
        """Return a copy with ``description`` updated."""
        return self._copy(description=description)

    def set_version(self, version: str | PromptVersion) -> MessageMetadata:
        """Return a copy with ``version`` as a string."""
        if isinstance(version, PromptVersion):
            version = str(version)
        if version is None:
            raise TypeError("version cannot be None")
        return self._copy(version=version)

    def set_tags(self, tags: Iterable[str]) -> MessageMetadata:
        """Replace the tag list."""
        return self._copy(tags=list(tags))

    def add_tag(self, tag: str) -> MessageMetadata:
        """Append one tag, keeping existing tags."""
        return self.set_tags([*self.tags, tag])

    def set_author(self, author: str) -> MessageMetadata:
        """Return a copy with ``author`` updated."""
        return self._copy(author=author)

    def set_category(self, category: str) -> MessageMetadata:
        """Return a copy with ``category`` updated."""
        return self._copy(category=category)

    def set_language(self, language: str) -> MessageMetadata:
        """Return a copy with ``language`` updated."""
        return self._copy(language=language)

    def set_provider(self, provider: str) -> MessageMetadata:
        """Hint which vendor this prompt was written for (informational)."""
        return self._copy(provider=provider)

    def set_model(self, model: str) -> MessageMetadata:
        """Hint which model this prompt was written for (informational)."""
        return self._copy(model=model)

    def set_min_compatible_version(
        self, min_version: str | PromptVersion
    ) -> MessageMetadata:
        """Lowest library/document version this metadata claims to work with."""
        if isinstance(min_version, PromptVersion):
            min_version = str(min_version)
        if min_version is None:
            raise TypeError("min_version cannot be None")
        return self._copy(min_compatible_version=min_version)
