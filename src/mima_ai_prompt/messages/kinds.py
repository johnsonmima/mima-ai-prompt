"""Typed messages for system, developer, user, assistant, tool, and function roles."""

from __future__ import annotations

from typing import Iterable

from mima_ai_prompt.messages.base import Message
from mima_ai_prompt.models import MessageAnnotation, MessageMetadata, ToolCall
from mima_ai_prompt.roles import MessageRole


class SystemMessage(Message):
    """System instructions that apply for the rest of the prompt."""

    def __init__(
        self,
        content: str | None = None,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        parts: Iterable[object] | None = None,
        name: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
    ) -> None:
        super().__init__(
            MessageRole.System,
            content,
            parts,
            metadata,
            id,
            name,
            annotations,
        )

    @classmethod
    def create(
        cls,
        content: str | Iterable[object],
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        name: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
    ) -> SystemMessage:
        """Create a system message from text or content parts."""
        if isinstance(content, str):
            return cls(
                content=content,
                metadata=metadata,
                id=id,
                name=name,
                annotations=annotations,
            )
        return cls(
            parts=content,
            metadata=metadata,
            id=id,
            name=name,
            annotations=annotations,
        )


class DeveloperMessage(Message):
    """Developer notes that sit between system and user turns."""

    def __init__(
        self,
        content: str | None = None,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        parts: Iterable[object] | None = None,
    ) -> None:
        super().__init__(MessageRole.Developer, content, parts, metadata, id)

    @classmethod
    def create(
        cls,
        content: str | Iterable[object],
        metadata: MessageMetadata | None = None,
        id: str | None = None,
    ) -> DeveloperMessage:
        """Build from a string or from content parts."""
        if isinstance(content, str):
            return cls(content=content, metadata=metadata, id=id)
        return cls(parts=content, metadata=metadata, id=id)


class UserMessage(Message):
    """User turn: text and/or image parts, optional speaker ``name``."""

    def __init__(
        self,
        content: str | None = None,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        parts: Iterable[object] | None = None,
        name: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
    ) -> None:
        super().__init__(
            MessageRole.User, content, parts, metadata, id, name, annotations
        )

    @classmethod
    def create(
        cls,
        content: str | Iterable[object],
        metadata: MessageMetadata | None = None,
        name: str | None = None,
        id: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
    ) -> UserMessage:
        """Create a user message from text or content parts."""
        if isinstance(content, str):
            return cls(
                content=content,
                metadata=metadata,
                id=id,
                name=name,
                annotations=annotations,
            )
        return cls(
            parts=content,
            metadata=metadata,
            id=id,
            name=name,
            annotations=annotations,
        )


class AssistantMessage(Message):
    """Assistant turn: text, tool calls, and/or a refusal."""

    def __init__(
        self,
        content: str | None = None,
        parts: Iterable[object] | None = None,
        tool_calls: Iterable[ToolCall] | None = None,
        refusal: str | None = None,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        name: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
    ) -> None:
        tool_list = list(tool_calls) if tool_calls is not None else []
        part_list = list(parts) if parts is not None else []
        allow_empty = (
            bool(tool_list) or bool(refusal and refusal.strip()) or bool(part_list)
        )
        super().__init__(
            MessageRole.Assistant,
            content,
            parts,
            metadata,
            id,
            name,
            annotations,
            allow_empty_body=allow_empty,
        )
        self.tool_calls = tool_list
        self.refusal = refusal.strip() if refusal and refusal.strip() else None

    @classmethod
    def create(
        cls,
        content: str | Iterable[object],
        metadata: MessageMetadata | None = None,
    ) -> AssistantMessage:
        """Build from a string or from content parts."""
        if isinstance(content, str):
            return cls.create_detailed(content=content, metadata=metadata)
        return cls.create_detailed(parts=content, metadata=metadata)

    @classmethod
    def create_with_tool_calls(
        cls,
        tool_calls: Iterable[ToolCall],
        content: str | None = None,
        metadata: MessageMetadata | None = None,
    ) -> AssistantMessage:
        """Assistant message that requests ``tool_calls``, with optional text."""
        return cls.create_detailed(
            content=content, tool_calls=tool_calls, metadata=metadata
        )

    @classmethod
    def create_refusal(
        cls, refusal: str, metadata: MessageMetadata | None = None
    ) -> AssistantMessage:
        """Assistant message whose body is a refusal (empty text is allowed)."""
        return cls.create_detailed(refusal=refusal, metadata=metadata)

    @classmethod
    def create_detailed(
        cls,
        content: str | None = None,
        parts: Iterable[object] | None = None,
        tool_calls: Iterable[ToolCall] | None = None,
        refusal: str | None = None,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        name: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
    ) -> AssistantMessage:
        """Full constructor: text, parts, tool calls, refusal, id, name, annotations."""
        return cls(
            content,
            parts,
            tool_calls,
            refusal,
            metadata,
            id,
            name,
            annotations,
        )


class ToolMessage(Message):
    """Tool result for ``tool_call_id``."""

    def __init__(
        self,
        tool_call_id: str,
        content: str,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
    ) -> None:
        if not tool_call_id or not str(tool_call_id).strip():
            raise ValueError("Tool call ID cannot be null or empty.")
        super().__init__(MessageRole.Tool, content, metadata=metadata, id=id)
        self.tool_call_id = tool_call_id

    @classmethod
    def create(
        cls,
        tool_call_id: str,
        content: str,
        metadata: MessageMetadata | None = None,
    ) -> ToolMessage:
        """Build a tool result for ``tool_call_id``."""
        return cls(tool_call_id, content, metadata)


class FunctionMessage(Message):
    """Legacy function-role result keyed by ``function_name``."""

    def __init__(
        self,
        function_name: str,
        content: str,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
    ) -> None:
        if not function_name or not str(function_name).strip():
            raise ValueError("Function name cannot be null or empty.")
        super().__init__(MessageRole.Function, content, metadata=metadata, id=id)
        self.function_name = function_name

    @classmethod
    def create(
        cls,
        function_name: str,
        content: str,
        metadata: MessageMetadata | None = None,
    ) -> FunctionMessage:
        """Build a function-role result for ``function_name``."""
        return cls(function_name, content, metadata)
