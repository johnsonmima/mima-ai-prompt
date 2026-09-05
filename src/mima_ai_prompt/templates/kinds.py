"""Role-specific templates for system, user, assistant, and developer messages."""

from __future__ import annotations

from typing import Iterable

from mima_ai_prompt.messages import (
    AssistantMessage,
    DeveloperMessage,
    SystemMessage,
    UserMessage,
)
from mima_ai_prompt.models import MessageMetadata, PromptVariable
from mima_ai_prompt.roles import MessageRole
from mima_ai_prompt.templates.base import MessageTemplate


def _create_fields(
    name_or_content: str,
    template_content: str | MessageMetadata | None,
    variable_defs: Iterable[PromptVariable] | None,
) -> tuple[str, MessageMetadata | None, Iterable[PromptVariable] | None]:
    """``create(content)``, ``create(content, metadata)``, or ``create(name, content)``."""
    if isinstance(template_content, MessageMetadata) or template_content is None:
        return name_or_content, template_content, variable_defs
    return (
        template_content,
        MessageMetadata.with_name(name_or_content),
        variable_defs,
    )


class SystemTemplate(MessageTemplate):
    """Renders a system-role message from template text."""

    def __init__(
        self,
        template_content: str,
        metadata: MessageMetadata | None = None,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> None:
        super().__init__(MessageRole.System, template_content, metadata, variable_defs)

    @classmethod
    def create(
        cls,
        name_or_content: str,
        template_content: str | MessageMetadata | None = None,
        *,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> SystemTemplate:
        """Create a system template from content, or name plus content."""
        content, metadata, defs = _create_fields(
            name_or_content, template_content, variable_defs
        )
        return cls(content, metadata, defs)

    def _create_message(self, rendered_content: str) -> SystemMessage:
        return SystemMessage(rendered_content, self.metadata)


class UserTemplate(MessageTemplate):
    """Renders a user-role message from template text."""

    def __init__(
        self,
        template_content: str,
        metadata: MessageMetadata | None = None,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> None:
        super().__init__(MessageRole.User, template_content, metadata, variable_defs)

    @classmethod
    def create(
        cls,
        name_or_content: str,
        template_content: str | MessageMetadata | None = None,
        *,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> UserTemplate:
        """Create a user template from content, or name plus content."""
        content, metadata, defs = _create_fields(
            name_or_content, template_content, variable_defs
        )
        return cls(content, metadata, defs)

    def _create_message(self, rendered_content: str) -> UserMessage:
        return UserMessage(rendered_content, self.metadata)


class AssistantTemplate(MessageTemplate):
    """Renders an assistant-role message from template text."""

    def __init__(
        self,
        template_content: str,
        metadata: MessageMetadata | None = None,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> None:
        super().__init__(MessageRole.Assistant, template_content, metadata, variable_defs)

    @classmethod
    def create(
        cls,
        name_or_content: str,
        template_content: str | MessageMetadata | None = None,
        *,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> AssistantTemplate:
        """Create an assistant template from content, or name plus content."""
        content, metadata, defs = _create_fields(
            name_or_content, template_content, variable_defs
        )
        return cls(content, metadata, defs)

    def _create_message(self, rendered_content: str) -> AssistantMessage:
        return AssistantMessage.create(rendered_content, self.metadata)


class DeveloperTemplate(MessageTemplate):
    """Renders a developer-role message from template text."""

    def __init__(
        self,
        template_content: str,
        metadata: MessageMetadata | None = None,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> None:
        super().__init__(MessageRole.Developer, template_content, metadata, variable_defs)

    @classmethod
    def create(
        cls,
        name_or_content: str,
        template_content: str | MessageMetadata | None = None,
        *,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> DeveloperTemplate:
        """Create a developer template from content, or name plus content."""
        content, metadata, defs = _create_fields(
            name_or_content, template_content, variable_defs
        )
        return cls(content, metadata, defs)

    def _create_message(self, rendered_content: str) -> DeveloperMessage:
        return DeveloperMessage(rendered_content, self.metadata)
