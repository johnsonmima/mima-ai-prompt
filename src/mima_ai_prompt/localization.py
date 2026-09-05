"""Locale-specific template strings with fallback to a default, then first entry."""

from __future__ import annotations

from typing import Mapping

from mima_ai_prompt.models import MessageMetadata
from mima_ai_prompt.roles import MessageRole
from mima_ai_prompt.templates import (
    AssistantTemplate,
    DeveloperTemplate,
    SystemTemplate,
    UserTemplate,
)


class LocalizedTemplate:
    """Several locale → template-text variants for one role.

    Lookup is case-insensitive: exact locale, then ``default_locale`` (``en``),
    then the first locale that was added.
    """

    def __init__(
        self, role: MessageRole, metadata: MessageMetadata | None = None
    ) -> None:
        if role is None:
            raise TypeError("role cannot be None")
        self.role = role
        self.metadata = metadata or MessageMetadata.empty()
        self._localized: dict[str, str] = {}
        self._default_locale = "en"

    @property
    def available_locales(self) -> list[str]:
        """Locales that currently have content, in insertion order."""
        return list(self._localized.keys())

    @property
    def default_locale(self) -> str:
        """Locale used when the requested one is missing."""
        return self._default_locale

    @classmethod
    def create(
        cls, role: MessageRole, metadata: MessageMetadata | None = None
    ) -> LocalizedTemplate:
        """Empty localized set for ``role``."""
        return cls(role, metadata)

    def add_locale(self, locale: str, content: str) -> LocalizedTemplate:
        """Store ``content`` for ``locale`` (replaces a prior same-locale entry)."""
        if not locale or not str(locale).strip():
            raise ValueError("Locale cannot be empty.")
        if not content or not str(content).strip():
            raise ValueError("Content cannot be empty.")
        key = locale.strip()
        for existing in list(self._localized):
            if existing.lower() == key.lower():
                del self._localized[existing]
                break
        self._localized[key] = content
        return self

    def with_default(self, locale: str) -> LocalizedTemplate:
        """Set the fallback locale used by ``get_content`` / ``render``."""
        self._default_locale = locale
        return self

    def with_metadata(self, metadata: MessageMetadata) -> LocalizedTemplate:
        """Attach metadata copied onto rendered messages."""
        self.metadata = metadata
        return self

    def get_content(self, locale: str) -> str:
        """Resolve template text for ``locale`` using the fallback chain."""
        for key, value in self._localized.items():
            if key.lower() == locale.lower():
                return value
        for key, value in self._localized.items():
            if key.lower() == self._default_locale.lower():
                return value
        if self._localized:
            return next(iter(self._localized.values()))
        raise RuntimeError("No localized content has been added.")

    def render(self, locale: str, variables: Mapping[str, object]) -> object:
        """Pick locale text, then render it as a system/user/assistant/developer message."""
        content = self.get_content(locale)
        if self.role == MessageRole.System:
            template = SystemTemplate.create(content, self.metadata)
        elif self.role == MessageRole.User:
            template = UserTemplate.create(content, self.metadata)
        elif self.role == MessageRole.Assistant:
            template = AssistantTemplate.create(content, self.metadata)
        elif self.role == MessageRole.Developer:
            template = DeveloperTemplate.create(content, self.metadata)
        else:
            raise RuntimeError(
                "LocalizedTemplate only supports system, user, assistant, and developer roles."
            )
        return template.render(variables)

    def has_locale(self, locale: str) -> bool:
        """True if ``locale`` was added (case-insensitive)."""
        return any(k.lower() == locale.lower() for k in self._localized)
