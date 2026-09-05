"""One assistant-requested tool invocation."""

from __future__ import annotations


class ToolCall:
    """Tool ``id``, function ``name``, and ``arguments_json`` (default ``{}``)."""

    def __init__(self, id: str, name: str, arguments_json: str = "{}") -> None:
        if not id or not str(id).strip():
            raise ValueError("Tool call id cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Tool call name cannot be empty.")
        self.id = id.strip()
        self.name = name.strip()
        self.arguments_json = (
            "{}"
            if not arguments_json or not str(arguments_json).strip()
            else arguments_json
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ToolCall)
            and self.id == other.id
            and self.name == other.name
            and self.arguments_json == other.arguments_json
        )

    def __hash__(self) -> int:
        return hash((self.id, self.name, self.arguments_json))

    @classmethod
    def create(cls, id: str, name: str, arguments_json: str = "{}") -> ToolCall:
        """Build a tool call; empty arguments become ``{}``."""
        return cls(id, name, arguments_json)
