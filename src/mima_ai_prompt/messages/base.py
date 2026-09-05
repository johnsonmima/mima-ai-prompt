"""Base message type and content-part normalization helpers."""

from __future__ import annotations

from typing import Iterable

from mima_ai_prompt._utils import new_id
from mima_ai_prompt.content import ContentPart, TextPart
from mima_ai_prompt.exceptions import PromptValidationException
from mima_ai_prompt.models import MessageAnnotation, MessageMetadata
from mima_ai_prompt.roles import MessageRole


class Message:
    """Typed chat message: role, parts, optional name, annotations, and metadata."""

    def __init__(
        self,
        role: MessageRole,
        content: str | None = None,
        parts: Iterable[ContentPart] | None = None,
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        name: str | None = None,
        annotations: Iterable[MessageAnnotation] | None = None,
        allow_empty_body: bool = False,
    ) -> None:
        if role is None:
            raise TypeError("role cannot be None")
        part_list = normalize_parts(content, parts, allow_empty_body)
        self.role = role
        self.parts: tuple[ContentPart, ...] = tuple(part_list)
        self.content = "".join(p.text for p in part_list if isinstance(p, TextPart))
        self.name = name.strip() if name and name.strip() else None
        self.annotations = list(annotations) if annotations is not None else []
        self.metadata = metadata or MessageMetadata.empty()
        self.id = id or new_id()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return NotImplemented
        return (
            self.id == other.id
            and self.role == other.role
            and self.content == other.content
            and self.name == other.name
            and self.parts == other.parts
            and self.annotations == other.annotations
            and getattr(self, "tool_calls", ()) == getattr(other, "tool_calls", ())
            and getattr(self, "refusal", None) == getattr(other, "refusal", None)
            and getattr(self, "tool_call_id", None)
            == getattr(other, "tool_call_id", None)
            and getattr(self, "function_name", None)
            == getattr(other, "function_name", None)
        )

    def __hash__(self) -> int:
        return hash((self.id, self.role, self.content, self.name))

    def __str__(self) -> str:
        if not self.content:
            preview = f"[{len(self.parts)} part(s)]"
        else:
            preview = self.content[:50]
        return f"[{self.role.name}] {preview}"


def require_message(message: object, *, name: str = "message") -> Message:
    if message is None:
        raise TypeError(f"{name} cannot be None")
    if not isinstance(message, Message):
        raise TypeError(f"{name} must be a Message instance.")
    return message


def normalize_parts(
    content: str | None,
    parts: Iterable[ContentPart] | None,
    allow_empty_body: bool,
) -> list[ContentPart]:
    part_list = [p for p in (parts or []) if p is not None]
    if not part_list:
        if content is not None and str(content).strip():
            part_list.append(TextPart(content))
        elif not allow_empty_body:
            raise PromptValidationException("Message content cannot be null or empty.")
    elif (
        content is not None
        and str(content).strip()
        and not any(isinstance(p, TextPart) for p in part_list)
    ):
        part_list.insert(0, TextPart(content))
    return part_list
