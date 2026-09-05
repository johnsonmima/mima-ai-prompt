"""Port of RichMessageTests.cs."""

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    ImagePart,
    PromptBuilder,
    PromptSerializer,
    TextPart,
    ToolCall,
    ToolMessage,
    UserMessage,
)


def test_user_message_text_create_has_single_text_part():
    message = UserMessage.create("Hello")
    assert len(message.parts) == 1
    assert isinstance(message.parts[0], TextPart)
    assert message.content == "Hello"


def test_image_part_from_base64_requires_media_type():
    part = ImagePart.from_base64("abc123", "image/png", detail="low")
    assert part.base64_data == "abc123"
    with pytest.raises(ValueError):
        ImagePart.from_base64("abc", "  ")


def test_image_part_requires_url_or_base64():
    with pytest.raises(ValueError):
        ImagePart.from_url("  ")
    with pytest.raises(TypeError):
        ImagePart.from_url(None)


def test_builder_add_user_with_image_and_parts():
    prompt = (
        PromptBuilder.create()
        .add_user_with_image("Look", "https://example.com/a.png")
        .build()
    )
    image_parts = [
        p for p in prompt.last_user_message.parts if isinstance(p, ImagePart)
    ]
    assert len(image_parts) == 1


def test_assistant_refusal_allows_empty_text():
    refusal = AssistantMessage.create_refusal("I can't help with that.")
    assert "can't" in refusal.refusal
    assert refusal.content == ""


def test_serializer_round_trips_image_base64_and_tool_calls():
    prompt = (
        PromptBuilder.create()
        .add_user(
            [TextPart.create("See"), ImagePart.from_base64("abc123", "image/png")]
        )
        .add_assistant_tool_calls([ToolCall.create("call_1", "get_weather", "{}")])
        .add_tool("call_1", "{}")
        .build()
    )
    serializer = PromptSerializer()
    raw = serializer.serialize(prompt)
    assert "abc123" in raw and "call_1" in raw
    restored = serializer.deserialize_prompt(raw)
    assert sum(1 for m in restored.messages if isinstance(m, ToolMessage)) == 1


def test_serializer_round_trips_image_and_name():
    message = UserMessage.create(
        [TextPart.create("Hi"), ImagePart.from_url("https://example.com/a.png")],
        name="alice",
    )
    serializer = PromptSerializer()
    restored = serializer.deserialize_message(serializer.serialize_message(message))
    assert restored.name == "alice"
    image = next(p for p in restored.parts if isinstance(p, ImagePart))
    assert "example.com" in image.url
