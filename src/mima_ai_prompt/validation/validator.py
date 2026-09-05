"""Empty bodies, duplicate ids, unmatched tool results, and common ordering issues."""

from __future__ import annotations

from mima_ai_prompt.messages import AssistantMessage, ToolMessage
from mima_ai_prompt.models import Prompt
from mima_ai_prompt.roles import MessageRole
from mima_ai_prompt.validation.report import PromptValidationReport


class PromptValidator:
    """Walk a prompt and return ``PromptValidationReport``."""

    def validate(self, prompt: Prompt) -> PromptValidationReport:
        """Return errors and warnings for a prompt-like object."""
        if prompt is None:
            raise TypeError("prompt cannot be None")

        errors: list[str] = []
        warnings: list[str] = []

        if prompt.message_count == 0:
            errors.append("Prompt must contain at least one message.")
            return PromptValidationReport(False, errors, warnings)

        seen_ids: set[str] = set()
        declared_tool_ids: set[str] = set()

        for msg in prompt.messages:
            msg_id = getattr(msg, "id", None)
            if msg_id:
                if msg_id in seen_ids:
                    errors.append(f"Duplicate message id '{msg_id}'.")
                seen_ids.add(msg_id)

            has_parts = len(getattr(msg, "parts", [])) > 0
            assistant_ok = False
            if isinstance(msg, AssistantMessage):
                assistant_ok = bool(msg.tool_calls) or bool(msg.refusal)
                for call in msg.tool_calls:
                    declared_tool_ids.add(call.id)
            content = getattr(msg, "content", "") or ""
            if not str(content).strip() and not has_parts and not assistant_ok:
                errors.append(f"Message with role '{msg.role.name}' has empty content.")

            if (
                isinstance(msg, ToolMessage)
                and msg.tool_call_id not in declared_tool_ids
            ):
                errors.append(
                    f"Tool message '{msg.tool_call_id}' does not match a preceding assistant tool call."
                )

        system_indexes = [
            i for i, m in enumerate(prompt.messages) if m.role == MessageRole.System
        ]
        if system_indexes and system_indexes[0] > 0:
            warnings.append(
                "System message should typically be the first message in a prompt."
            )

        system_count = sum(1 for m in prompt.messages if m.role == MessageRole.System)
        if system_count > 1:
            warnings.append(
                f"Prompt contains {system_count} system messages. "
                "Most providers expect at most one."
            )

        has_user = any(m.role == MessageRole.User for m in prompt.messages)
        if not has_user:
            warnings.append(
                "Prompt does not contain a user message. Most providers expect at least one."
            )

        if prompt.message_count > 100:
            warnings.append(
                f"Prompt contains {prompt.message_count} messages. "
                "Consider reducing for performance."
            )

        return PromptValidationReport(len(errors) == 0, errors, warnings)
