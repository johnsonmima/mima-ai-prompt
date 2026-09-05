"""Port of PartsAndContentContractTests.cs."""

import json

import pytest

from mima_ai_prompt import (
    ImagePart,
    PromptBuilder,
    PromptSerializer,
    TextPart,
    UserMessage,
)


def test_content_is_concatenated_text_parts_not_a_second_body():
    message = UserMessage.create(
        [
            TextPart.create("Look at "),
            ImagePart.from_url("https://example.com/a.png"),
            TextPart.create("this."),
        ]
    )
    assert len(message.parts) == 3
    assert message.content == "Look at this."


def test_serialize_writes_parts_only_does_not_repeat_text_under_content():
    prompt = (
        PromptBuilder.system(
            "You are a support agent for Billing. Be concise. Never invent policy."
        )
        .add_user("Why was I charged twice?")
        .build()
    )
    serializer = PromptSerializer()
    raw = serializer.serialize(prompt)
    doc = json.loads(raw)
    for message in doc["messages"]:
        assert "content" not in message
        assert "parts" in message
        assert len(message["parts"]) > 0
        assert message["parts"][0]["type"] == "text"
        assert "text" in message["parts"][0]
    assert "You are a support agent for Billing" in raw
    assert "Why was I charged twice?" in raw


def test_round_trip_restores_parts_and_recomputes_content():
    original = UserMessage.create(
        [
            TextPart.create("Caption"),
            ImagePart.from_url("https://example.com/a.png"),
        ]
    )
    serializer = PromptSerializer()
    raw = serializer.serialize_message(original)
    assert '"content"' not in raw
    restored = serializer.deserialize_message(raw)
    text_parts = [p for p in restored.parts if isinstance(p, TextPart)]
    image_parts = [p for p in restored.parts if isinstance(p, ImagePart)]
    assert len(text_parts) == 1 and text_parts[0].text == "Caption"
    assert len(image_parts) == 1 and image_parts[0].url == "https://example.com/a.png"
    assert restored.content == "Caption"


def test_deserialize_content_string_without_parts_throws():
    raw = '{"role": "user", "content": "Why was I charged twice?", "id": "invalid"}'
    with pytest.raises(ValueError, match="parts"):
        PromptSerializer().deserialize_message(raw)
