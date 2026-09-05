"""Role-specific templates with variable discovery, validation, and rendering."""

from mima_ai_prompt.templates.base import MessageTemplate
from mima_ai_prompt.templates.kinds import (
    AssistantTemplate,
    DeveloperTemplate,
    SystemTemplate,
    UserTemplate,
)

__all__ = [
    "AssistantTemplate",
    "DeveloperTemplate",
    "MessageTemplate",
    "SystemTemplate",
    "UserTemplate",
]
