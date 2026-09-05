"""Port of CoverageGapTests.cs."""

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    Conversation,
    ImagePart,
    MessageAnnotation,
    MessageRole,
    OutputFormat,
    PromptBuilder,
    PromptSerializer,
    PromptValidationException,
    TextPart,
    ToolCall,
    UserMessage,
)


def test_message_annotation_factories_and_empty_kind():
    url = MessageAnnotation.url_citation("https://example.com", "Title", "quote", 1, 2)
    assert url.kind == "url_citation"
    assert url.url == "https://example.com"
    assert url.title == "Title"
    assert url.quote == "quote"
    assert url.start_index == 1
    assert url.end_index == 2

    file = MessageAnnotation.file_citation("file-1", "Doc", "excerpt")
    assert file.kind == "file_citation"
    assert file.file_id == "file-1"

    internal_ref = MessageAnnotation.internal_ref("ref-9", "Internal")
    assert internal_ref.kind == "internal_ref"
    assert internal_ref.file_id == "ref-9"

    with pytest.raises(ValueError):
        MessageAnnotation("  ")


def test_tool_call_whitespace_arguments_become_empty_object():
    call = ToolCall.create("id-1", "weather", "  ")
    assert call.arguments_json == "{}"
    with pytest.raises(ValueError):
        ToolCall(" ", "n")
    with pytest.raises(ValueError):
        ToolCall("id", " ")


def test_text_part_type_and_null_text():
    part = TextPart.create("hi")
    assert part.type == "text"
    assert part.text == "hi"
    with pytest.raises(TypeError):
        TextPart(None)


def test_image_part_type_url_detail_and_base64():
    url = ImagePart.from_url("https://example.com/a.png", "high")
    assert url.type == "image"
    assert url.detail == "high"
    b64 = ImagePart.from_base64("abc", "image/jpeg", "low")
    assert b64.media_type == "image/jpeg"
    assert b64.detail == "low"


def test_conversation_parts_assistant_message_and_window():
    conversation = (
        Conversation.create("Chat")
        .add_user([TextPart.create("Look")])
        .add_assistant(AssistantMessage.create("Seen"))
    )
    assert len(conversation.to_prompt().messages) == 2
    assert len(conversation.to_prompt_with_window(1).messages) == 1
    with pytest.raises(TypeError):
        conversation.add_user(None)
    with pytest.raises((TypeError, PromptValidationException)):
        conversation.add_assistant(None)


def test_prompt_builder_parts_roles_response_format_and_use_message():
    parts = [TextPart.create("hello")]
    prompt = (
        PromptBuilder.create()
        .add_system(parts)
        .add_developer(parts)
        .add_user(parts)
        .add_assistant(parts)
        .add(MessageRole.User, "again")
        .with_response_format(OutputFormat.json())
        .build()
    )
    assert prompt.response_format.type == OutputFormat.JSON
    assert len(prompt.messages) == 5

    from_message = PromptBuilder.use(UserMessage("hi")).build()
    assert len(from_message.messages) == 1

    with pytest.raises(ValueError):
        PromptBuilder.create().add(MessageRole.Tool, "x")
    with pytest.raises(TypeError):
        PromptBuilder.create().add(None, "x")
    with pytest.raises(TypeError):
        PromptBuilder.create().add_system(None)
    with pytest.raises(TypeError):
        PromptBuilder.create().add_assistant(None)
    with pytest.raises(TypeError):
        PromptBuilder.create().add_developer(None)


def test_serializer_round_trips_annotations_and_yaml_schema():
    annotated = AssistantMessage.create_detailed(
        content="See source",
        annotations=[MessageAnnotation.url_citation("https://example.com", "Ex")],
    )
    prompt = (
        PromptBuilder.create()
        .add_user("q")
        .add_message(annotated)
        .with_response_format(OutputFormat.yaml_with_schema("title: string"))
        .build()
    )
    serializer = PromptSerializer()
    restored = serializer.deserialize_prompt(serializer.serialize(prompt))
    assistants = [m for m in restored.messages if isinstance(m, AssistantMessage)]
    assert len(assistants) == 1
    assert any(a.kind == "url_citation" for a in assistants[0].annotations)
    fmt = restored.response_format
    assert fmt.type == OutputFormat.YAML
    assert "title" in fmt.schema
