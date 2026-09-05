"""Fluent builder for assembling prompts, examples, history, and response formats."""

from __future__ import annotations

from typing import Iterable

from mima_ai_prompt.content import ContentPart, ImagePart, TextPart
from mima_ai_prompt.exceptions import PromptValidationException
from mima_ai_prompt.messages import (
    AssistantMessage,
    DeveloperMessage,
    FunctionMessage,
    Message,
    SystemMessage,
    ToolMessage,
    UserMessage,
)
from mima_ai_prompt.messages.base import require_message
from mima_ai_prompt.models import (
    MessageMetadata,
    OutputFormat,
    Prompt,
    PromptConstraints,
    ToolCall,
)
from mima_ai_prompt.roles import MessageRole
from mima_ai_prompt.templates import MessageTemplate


class PromptBuilder:
    """Fluently assembles typed messages and template values into a prompt."""

    def __init__(self) -> None:
        self._items: list[Message | MessageTemplate] = []
        self._variables: dict[str, object] = {}
        self._metadata: MessageMetadata | None = None
        self._response_format: OutputFormat | None = None
        self._constraints: PromptConstraints | None = None

    @classmethod
    def system(cls, content: str) -> PromptBuilder:
        """Start a builder with a system message."""
        builder = cls()
        builder._items.append(SystemMessage(content))
        return builder

    @classmethod
    def use(cls, template_or_message: Message | MessageTemplate) -> PromptBuilder:
        """Start a builder with an existing template or message."""
        if template_or_message is None:
            raise TypeError("template_or_message cannot be None")
        builder = cls()
        if isinstance(template_or_message, MessageTemplate):
            builder._items.append(template_or_message)
        else:
            builder._items.append(
                require_message(template_or_message, name="template_or_message")
            )
        return builder

    @classmethod
    def create(cls) -> PromptBuilder:
        """Create an empty builder."""
        return cls()

    def add_system(self, content: str | Iterable[ContentPart]) -> PromptBuilder:
        """Append a system message."""
        if isinstance(content, str):
            self._items.append(SystemMessage(content))
        else:
            if content is None:
                raise TypeError("parts cannot be None")
            self._items.append(SystemMessage.create(content))
        return self

    def add_developer(self, content: str | Iterable[ContentPart]) -> PromptBuilder:
        """Append a developer message."""
        if isinstance(content, str):
            self._items.append(DeveloperMessage(content))
        else:
            if content is None:
                raise TypeError("parts cannot be None")
            self._items.append(DeveloperMessage.create(content))
        return self

    def add_user(
        self, content: str | Iterable[ContentPart], name: str | None = None
    ) -> PromptBuilder:
        """Append a user message. ``name`` is applied for both text and parts."""
        if isinstance(content, str):
            self._items.append(UserMessage(content, name=name))
        else:
            if content is None:
                raise TypeError("parts cannot be None")
            self._items.append(UserMessage.create(content, name=name))
        return self

    def add_user_with_image(
        self, text: str, image_url: str, name: str | None = None
    ) -> PromptBuilder:
        """Append a user message with text and an image URL."""
        self._items.append(
            UserMessage.create(
                [TextPart.create(text), ImagePart.from_url(image_url)], name=name
            )
        )
        return self

    def add_assistant(self, content: str | Iterable[ContentPart]) -> PromptBuilder:
        """Append an assistant message."""
        if isinstance(content, str):
            self._items.append(AssistantMessage(content))
        else:
            if content is None:
                raise TypeError("parts cannot be None")
            self._items.append(AssistantMessage.create(content))
        return self

    def add_assistant_tool_calls(
        self, tool_calls: Iterable[ToolCall], content: str | None = None
    ) -> PromptBuilder:
        """Append an assistant message that requests tool calls."""
        self._items.append(AssistantMessage.create_with_tool_calls(tool_calls, content))
        return self

    def add_tool(self, tool_call_id: str, content: str) -> PromptBuilder:
        """Append a tool result message."""
        self._items.append(ToolMessage(tool_call_id, content))
        return self

    def add_function(self, function_name: str, content: str) -> PromptBuilder:
        """Append a legacy function result message."""
        self._items.append(FunctionMessage(function_name, content))
        return self

    def add_message(self, message: Message) -> PromptBuilder:
        """Append an existing typed message."""
        self._items.append(require_message(message))
        return self

    def add(self, role: MessageRole, content: str) -> PromptBuilder:
        """Append a text message for a simple role (not tool/function)."""
        if role is None:
            raise TypeError("role cannot be None")
        if role == MessageRole.System:
            return self.add_system(content)
        if role == MessageRole.Developer:
            return self.add_developer(content)
        if role == MessageRole.User:
            return self.add_user(content)
        if role == MessageRole.Assistant:
            return self.add_assistant(content)
        if role in (MessageRole.Tool, MessageRole.Function):
            raise ValueError(
                f"Use add_tool / add_function for '{role.name}' (they require an id/name)."
            )
        raise ValueError(f"Unsupported role '{role.name}'.")

    def add_template(self, template: MessageTemplate) -> PromptBuilder:
        """Queue a template to render in call order at build time."""
        if template is None:
            raise TypeError("template cannot be None")
        self._items.append(template)
        return self

    def useWith(self, name: str, value: object) -> PromptBuilder:
        """Set a template variable. Unused names fail at build."""
        if not name or not str(name).strip():
            raise ValueError("Variable name cannot be null or empty.")
        if value is None:
            raise TypeError("value cannot be None")
        self._variables[name] = value
        return self

    def with_var(self, name: str, value: object) -> PromptBuilder:
        """Alias for ``useWith``."""
        return self.useWith(name, value)

    def with_metadata(self, metadata: MessageMetadata) -> PromptBuilder:
        """Set prompt-level metadata (replaced by later ``with_name``)."""
        self._metadata = metadata
        return self

    def with_name(self, name: str) -> PromptBuilder:
        """Set the prompt metadata name."""
        self._metadata = (self._metadata or MessageMetadata.empty()).set_name(name)
        return self

    def with_response_format(self, format: OutputFormat) -> PromptBuilder:
        """Set the requested output format."""
        if format is None:
            raise TypeError("format cannot be None")
        self._response_format = format
        return self

    def with_constraints(self, constraints: PromptConstraints) -> PromptBuilder:
        """Attach rendered constraints as a developer message at build time."""
        if constraints is None:
            raise TypeError("constraints cannot be None")
        self._constraints = constraints
        return self

    def add_example(self, user_content: str, assistant_content: str) -> PromptBuilder:
        """Append a user/assistant few-shot pair."""
        self._items.append(UserMessage(user_content))
        self._items.append(AssistantMessage(assistant_content))
        return self

    def add_history(self, history: Iterable[tuple[str, str]]) -> PromptBuilder:
        """Append user/assistant turns from history pairs."""
        for user, assistant in history:
            self._items.append(UserMessage(user))
            self._items.append(AssistantMessage(assistant))
        return self

    def build(self) -> Prompt:
        """Render templates in order and return the prompt."""
        all_messages: list[Message] = []
        used_names: set[str] = set()
        for item in self._items:
            if isinstance(item, MessageTemplate):
                needed = set(item.variables)
                subset: dict[str, object] = {
                    name: self._variables[name]
                    for name in needed
                    if name in self._variables
                }
                all_messages.append(item.render(subset))
                used_names.update(needed)
            else:
                all_messages.append(item)

        unused = [name for name in self._variables if name not in used_names]
        if unused:
            raise PromptValidationException(
                [f"Unused variable: '{name}'" for name in unused]
            )

        if self._constraints is not None:
            text = self._constraints.render()
            if text.strip():
                all_messages.append(DeveloperMessage(text))

        return Prompt(
            all_messages,
            self._metadata,
            response_format=self._response_format,
        )

    @classmethod
    def quick(cls, system_content: str, user_content: str) -> Prompt:
        """Create a prompt with one system and one user message."""
        return cls.create().add_system(system_content).add_user(user_content).build()

    @classmethod
    def user_only(cls, user_content: str) -> Prompt:
        """Create a prompt containing a single user message."""
        return cls.create().add_user(user_content).build()
