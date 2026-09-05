"""Converts prompts, messages, metadata, and templates to canonical JSON and back."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from mima_ai_prompt._utils import aware_utc
from mima_ai_prompt.content import ImagePart, TextPart
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
    MessageAnnotation,
    MessageMetadata,
    OutputFormat,
    Prompt,
    ToolCall,
)
from mima_ai_prompt.roles import MessageRole
from mima_ai_prompt.templates import (
    AssistantTemplate,
    DeveloperTemplate,
    MessageTemplate,
    SystemTemplate,
    UserTemplate,
)


def _dt_iso(value: datetime) -> str:
    return aware_utc(value).isoformat().replace("+00:00", "Z")


def _dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _metadata_dict(metadata: MessageMetadata) -> dict[str, Any]:
    return {
        "name": metadata.name,
        "description": metadata.description,
        "category": metadata.category,
        "version": metadata.version,
        "author": metadata.author,
        "tags": list(metadata.tags),
        "language": metadata.language,
        "provider": metadata.provider,
        "model": metadata.model,
        "created": _dt_iso(metadata.created),
        "modified": _dt_iso(metadata.modified),
        "minCompatibleVersion": metadata.min_compatible_version,
    }


def _part_dict(part: object) -> dict[str, Any]:
    if isinstance(part, TextPart):
        return {"type": "text", "text": part.text}
    if isinstance(part, ImagePart):
        return {
            "type": "image",
            "url": part.url,
            "base64Data": part.base64_data,
            "mediaType": part.media_type,
            "detail": part.detail,
        }
    raise TypeError(f"Unsupported content part: {type(part)!r}")


def _message_dict(message: Message) -> dict[str, Any]:
    dto: dict[str, Any] = {
        "role": message.role.name,
        "id": message.id,
        "name": message.name,
        "metadata": _metadata_dict(message.metadata),
        "parts": [_part_dict(p) for p in message.parts] if message.parts else None,
        "annotations": (
            [
                {
                    "kind": a.kind,
                    "url": a.url,
                    "fileId": a.file_id,
                    "title": a.title,
                    "quote": a.quote,
                    "startIndex": a.start_index,
                    "endIndex": a.end_index,
                }
                for a in message.annotations
            ]
            if message.annotations
            else None
        ),
    }
    if isinstance(message, ToolMessage):
        dto["toolCallId"] = message.tool_call_id
    elif isinstance(message, FunctionMessage):
        dto["functionName"] = message.function_name
    elif isinstance(message, AssistantMessage):
        dto["refusal"] = message.refusal
        dto["toolCalls"] = [
            {
                "id": t.id,
                "name": t.name,
                "argumentsJson": t.arguments_json,
            }
            for t in message.tool_calls
        ]
    return {k: v for k, v in dto.items() if v is not None or k in {"role", "id"}}


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def _from_metadata(dto: dict[str, Any] | None) -> MessageMetadata:
    if not dto:
        return MessageMetadata.empty()
    return MessageMetadata(
        name=dto.get("name"),
        description=dto.get("description"),
        category=dto.get("category"),
        version=dto.get("version"),
        author=dto.get("author"),
        tags=dto.get("tags") or [],
        language=dto.get("language"),
        provider=dto.get("provider"),
        model=dto.get("model"),
        created=_parse_dt(dto.get("created")),
        modified=_parse_dt(dto.get("modified")),
        min_compatible_version=dto.get("minCompatibleVersion"),
    )


def _from_part(dto: dict[str, Any]) -> object:
    if dto.get("type") == "image":
        url = dto.get("url")
        if url:
            return ImagePart.from_url(url, dto.get("detail"))
        return ImagePart.from_base64(
            dto.get("base64Data") or "",
            dto.get("mediaType") or "image/png",
            dto.get("detail"),
        )
    return TextPart(dto.get("text") or "")


def _from_format(dto: dict[str, Any] | None) -> OutputFormat | None:
    if not dto:
        return None
    type_name = dto.get("type") or ""
    instructions = dto.get("instructions") or ""
    schema = dto.get("schema")
    if schema:
        if type_name.lower() == OutputFormat.JSON:
            return OutputFormat.json_with_schema(schema)
        if type_name.lower() == OutputFormat.YAML:
            return OutputFormat.yaml_with_schema(schema)
    return OutputFormat.custom(type_name, instructions, schema)


def _from_message(dto: dict[str, Any]) -> Message:
    role = MessageRole.parse(dto["role"])
    metadata = _from_metadata(dto.get("metadata"))
    annotations = None
    if dto.get("annotations"):
        annotations = [
            MessageAnnotation(
                a["kind"],
                a.get("url"),
                a.get("fileId"),
                a.get("title"),
                a.get("quote"),
                a.get("startIndex"),
                a.get("endIndex"),
            )
            for a in dto["annotations"]
        ]
    parts = None
    if dto.get("parts"):
        parts = [_from_part(p) for p in dto["parts"]]

    tool_calls = None
    if dto.get("toolCalls"):
        tool_calls = [
            ToolCall(t["id"], t["name"], t.get("argumentsJson") or "{}")
            for t in dto["toolCalls"]
        ]

    allow_empty = role == MessageRole.Assistant and (
        bool(tool_calls) or bool(dto.get("refusal"))
    )
    if parts is None and not allow_empty:
        raise ValueError("Message JSON requires a non-empty parts array.")

    if role == MessageRole.System:
        if parts is None:
            raise ValueError("Message JSON requires a non-empty parts array.")
        return SystemMessage.create(
            parts, metadata, dto.get("id"), dto.get("name"), annotations
        )
    if role == MessageRole.Developer:
        if parts is None:
            raise ValueError("Message JSON requires a non-empty parts array.")
        return DeveloperMessage.create(parts, metadata, dto.get("id"))
    if role == MessageRole.User:
        if parts is None:
            raise ValueError("Message JSON requires a non-empty parts array.")
        return UserMessage.create(
            parts, metadata, dto.get("name"), dto.get("id"), annotations
        )
    if role == MessageRole.Assistant:
        return AssistantMessage.create_detailed(
            parts=parts,
            tool_calls=tool_calls,
            refusal=dto.get("refusal"),
            metadata=metadata,
            id=dto.get("id"),
            name=dto.get("name"),
            annotations=annotations,
        )

    text_body = "".join(p.text for p in (parts or []) if isinstance(p, TextPart))
    if role == MessageRole.Tool:
        tool_call_id = dto.get("toolCallId")
        if not tool_call_id or not str(tool_call_id).strip():
            raise ValueError("Tool message JSON requires toolCallId.")
        return ToolMessage(
            tool_call_id,
            text_body,
            metadata,
            dto.get("id"),
        )
    function_name = dto.get("functionName")
    if not function_name or not str(function_name).strip():
        raise ValueError("Function message JSON requires functionName.")
    return FunctionMessage(
        function_name,
        text_body,
        metadata,
        dto.get("id"),
    )


class PromptSerializer:
    """Compact, sorted-key JSON for prompts, messages, and templates.

    Bodies are stored as ``parts``. The in-memory ``content`` field is derived
    and is not written.
    """

    def serialize(self, prompt: Prompt) -> str:
        """Prompt → JSON string."""
        if prompt is None:
            raise TypeError("prompt cannot be None")
        dto: dict[str, Any] = {
            "id": prompt.id,
            "metadata": _metadata_dict(prompt.metadata),
            "messages": [_message_dict(m) for m in prompt.messages],
        }
        if prompt.response_format is not None:
            dto["responseFormat"] = {
                "type": prompt.response_format.type,
                "schema": prompt.response_format.schema,
                "instructions": prompt.response_format.instructions,
            }
        return _dumps(dto)

    def deserialize_prompt(self, json_text: str) -> Prompt:
        """JSON string → ``Prompt``."""
        if json_text is None or not str(json_text).strip():
            raise ValueError("JSON cannot be null or empty.")
        dto = json.loads(json_text)
        messages = [_from_message(m) for m in dto.get("messages", [])]
        return Prompt(
            messages,
            _from_metadata(dto.get("metadata")),
            dto.get("id"),
            _from_format(dto.get("responseFormat")),
        )

    def serialize_message(self, message: Message) -> str:
        """Serialize one message to canonical JSON."""
        typed = require_message(message)
        return _dumps(_message_dict(typed))

    def deserialize_message(self, json_text: str) -> Message:
        """JSON string → one ``Message``."""
        if json_text is None or not str(json_text).strip():
            raise ValueError("JSON cannot be null or empty.")
        return _from_message(json.loads(json_text))

    def serialize_template(self, template: MessageTemplate) -> str:
        """Template → JSON (role, text, discovered variables, metadata)."""
        if template is None:
            raise TypeError("template cannot be None")
        dto = {
            "role": template.role.name,
            "templateContent": template.template_content,
            "variables": template.variables,
            "metadata": _metadata_dict(template.metadata),
        }
        return _dumps(dto)

    def deserialize_template(self, json_text: str) -> MessageTemplate:
        """Deserialize template JSON into a role-specific template."""
        if json_text is None or not str(json_text).strip():
            raise ValueError("JSON cannot be null or empty.")
        dto = json.loads(json_text)
        role = MessageRole.parse(dto["role"])
        content = dto.get("templateContent")
        if content is None or not str(content).strip():
            raise ValueError("Template JSON requires templateContent.")
        metadata = _from_metadata(dto.get("metadata"))
        if role == MessageRole.System:
            return SystemTemplate(content, metadata)
        if role == MessageRole.User:
            return UserTemplate(content, metadata)
        if role == MessageRole.Assistant:
            return AssistantTemplate(content, metadata)
        if role == MessageRole.Developer:
            return DeveloperTemplate(content, metadata)
        raise ValueError(f"Unsupported template role '{role.name}'.")
