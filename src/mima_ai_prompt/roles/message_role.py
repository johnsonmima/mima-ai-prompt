"""Closed set of roles used to order and classify prompt messages."""

from __future__ import annotations

from typing import ClassVar


class MessageRole:
    """One of: system, developer, user, assistant, tool, function.

    ``name`` is the lowercase JSON value. Equality is by name.
    """

    name: str
    priority: int
    description: str
    is_built_in: bool = True

    System: ClassVar[MessageRole]
    Developer: ClassVar[MessageRole]
    User: ClassVar[MessageRole]
    Assistant: ClassVar[MessageRole]
    Tool: ClassVar[MessageRole]
    Function: ClassVar[MessageRole]

    def __init__(self, name: str, priority: int, description: str) -> None:
        self.name = name
        self.priority = priority
        self.description = description

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"MessageRole({self.name!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MessageRole) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    @staticmethod
    def parse(role_name: str) -> MessageRole:
        """Map a role string (any case) to a built-in ``MessageRole``."""
        if role_name is None or not str(role_name).strip():
            raise ValueError("Role name cannot be null or empty.")
        key = role_name.strip().lower()
        mapping = {
            "system": MessageRole.System,
            "developer": MessageRole.Developer,
            "user": MessageRole.User,
            "assistant": MessageRole.Assistant,
            "tool": MessageRole.Tool,
            "function": MessageRole.Function,
        }
        role = mapping.get(key)
        if role is None:
            raise ValueError(
                f"Unknown message role: '{role_name}'. "
                "Supported: system, developer, user, assistant, tool, function."
            )
        return role

    @staticmethod
    def try_parse(role_name: str | None) -> MessageRole | None:
        """Like ``parse``, but returns ``None`` instead of raising."""
        if role_name is None or not str(role_name).strip():
            return None
        try:
            return MessageRole.parse(role_name)
        except ValueError:
            return None

    @staticmethod
    def all() -> list[MessageRole]:
        """The six built-in roles in priority order."""
        return [
            MessageRole.System,
            MessageRole.Developer,
            MessageRole.User,
            MessageRole.Assistant,
            MessageRole.Tool,
            MessageRole.Function,
        ]


MessageRole.System = MessageRole(
    "system", 0, "Defines the AI's identity, behavior, and permanent rules."
)
MessageRole.Developer = MessageRole(
    "developer", 1, "Provides additional context between system and user."
)
MessageRole.User = MessageRole("user", 2, "Human user input and intent.")
MessageRole.Assistant = MessageRole("assistant", 3, "Previous AI responses.")
MessageRole.Tool = MessageRole("tool", 4, "Output from a tool invocation.")
MessageRole.Function = MessageRole("function", 5, "Legacy function call result.")
