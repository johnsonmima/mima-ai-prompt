"""Ordered typed messages and optional response format."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Sequence

from mima_ai_prompt._utils import new_id
from mima_ai_prompt.exceptions import PromptValidationException
from mima_ai_prompt.models.metadata import MessageMetadata
from mima_ai_prompt.models.output_format import OutputFormat
from mima_ai_prompt.roles import MessageRole

if TYPE_CHECKING:
    from mima_ai_prompt.messages import Message


class Prompt:
    """An ordered, immutable sequence of typed messages plus optional response format."""

    def __init__(
        self,
        messages: Iterable[Message],
        metadata: MessageMetadata | None = None,
        id: str | None = None,
        response_format: OutputFormat | None = None,
    ) -> None:
        from mima_ai_prompt.messages.base import require_message

        if messages is None:
            raise TypeError("messages cannot be None")
        message_list = [require_message(m, name="messages") for m in messages]
        if not message_list:
            raise PromptValidationException(
                "A prompt must contain at least one message."
            )
        self._messages: tuple[Message, ...] = tuple(message_list)
        self.metadata = metadata or MessageMetadata.empty()
        self.id = id or new_id()
        self.response_format = response_format

    @property
    def messages(self) -> Sequence[Message]:
        """Messages in send order (immutable)."""
        return self._messages

    @property
    def message_count(self) -> int:
        """Number of messages."""
        return len(self._messages)

    @property
    def system_message(self) -> Message | None:
        """First system message, if any."""
        return next((m for m in self._messages if m.role == MessageRole.System), None)

    @property
    def last_user_message(self) -> Message | None:
        """Last user message, if any."""
        users = [m for m in self._messages if m.role == MessageRole.User]
        return users[-1] if users else None

    def get_messages(self, role: MessageRole) -> list[Message]:
        """Return messages whose role matches."""
        return [m for m in self._messages if m.role == role]

    def __str__(self) -> str:
        return f"Prompt [{self.message_count} messages] {self.metadata.name or self.id}"
