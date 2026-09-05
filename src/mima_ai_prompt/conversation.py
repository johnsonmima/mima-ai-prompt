"""Conversation history that can be turned into a prompt."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4

from mima_ai_prompt.messages import AssistantMessage, Message, SystemMessage, UserMessage
from mima_ai_prompt.messages.base import require_message
from mima_ai_prompt.models import MessageMetadata, Prompt


class Conversation:
    """Named session: optional system message plus ordered user/assistant turns."""

    def __init__(self, name: str, id: str | None = None) -> None:
        self.name = name
        self.id = id or uuid4().hex
        self.created = datetime.now(timezone.utc)
        self._messages: list[Message] = []
        self._system_message: Message | None = None

    @property
    def messages(self) -> list[Message]:
        """Copy of history messages (excludes the system message)."""
        return list(self._messages)

    @property
    def system_message(self) -> Message | None:
        """System message used when converting to a prompt, if set."""
        return self._system_message

    @property
    def message_count(self) -> int:
        """Number of history messages, not counting the system message."""
        return len(self._messages)

    @classmethod
    def create(cls, name: str) -> Conversation:
        """Start an empty conversation with the given name."""
        return cls(name)

    def with_system(self, content: str) -> Conversation:
        """Set or replace the system message."""
        self._system_message = SystemMessage(content)
        return self

    def add_user(self, content: str | Iterable[object]) -> Conversation:
        """Append a user turn (text or content parts)."""
        if isinstance(content, str):
            self._messages.append(UserMessage(content))
        else:
            if content is None:
                raise TypeError("parts cannot be None")
            self._messages.append(UserMessage.create(content))
        return self

    def add_assistant(self, content: str | AssistantMessage) -> Conversation:
        """Append an assistant turn (text or an existing message)."""
        if isinstance(content, AssistantMessage):
            self._messages.append(content)
        else:
            self._messages.append(AssistantMessage(content))
        return self

    def add_message(self, message: Message) -> Conversation:
        """Append any typed message to history."""
        self._messages.append(require_message(message))
        return self

    def to_prompt(self) -> Prompt:
        """Build a prompt from the system message (if any) plus full history."""
        all_messages: list[Message] = []
        if self._system_message is not None:
            all_messages.append(self._system_message)
        all_messages.extend(self._messages)
        return Prompt(all_messages, MessageMetadata(name=self.name))

    def to_prompt_with_window(self, count: int) -> Prompt:
        """Build a prompt using only the last ``count`` history messages.

        ``count <= 0`` keeps the system message (if any) and drops history.
        """
        all_messages: list[Message] = []
        if self._system_message is not None:
            all_messages.append(self._system_message)
        take = max(0, count)
        if take == 0:
            recent: list[Message] = []
        elif take >= len(self._messages):
            recent = list(self._messages)
        else:
            recent = self._messages[-take:]
        all_messages.extend(recent)
        return Prompt(all_messages, MessageMetadata(name=self.name))
