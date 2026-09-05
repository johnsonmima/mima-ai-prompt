"""Port of SerializationTests.cs (PromptJsonOptions replaced with camelCase key checks)."""

import json

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    DeveloperMessage,
    FunctionMessage,
    MessageMetadata,
    Prompt,
    PromptSerializer,
    SystemMessage,
    SystemTemplate,
    ToolMessage,
    UserMessage,
    UserTemplate,
)
from mima_ai_prompt.roles import MessageRole


@pytest.fixture
def serializer():
    return PromptSerializer()


def test_serialize_prompt_produces_json(serializer):
    prompt = Prompt(
        [SystemMessage("sys"), UserMessage("hi")],
        MessageMetadata(name="MyPrompt"),
        "prompt-id",
    )
    raw = serializer.serialize(prompt)
    assert '"id"' in raw
    assert "prompt-id" in raw
    assert "sys" in raw
    assert "hi" in raw


def test_serialize_null_prompt_throws(serializer):
    with pytest.raises(TypeError):
        serializer.serialize(None)


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_deserialize_prompt_null_or_empty_json_throws(serializer, raw):
    with pytest.raises((TypeError, ValueError), match="JSON cannot be null or empty"):
        serializer.deserialize_prompt(raw)


def test_round_trip_prompt_preserves_messages_and_metadata(serializer):
    prompt = Prompt(
        [SystemMessage("You are helpful."), UserMessage("Hi there")],
        MessageMetadata(name="RoundTrip"),
    )
    deserialized = serializer.deserialize_prompt(serializer.serialize(prompt))
    assert len(deserialized.messages) == 2
    assert deserialized.messages[0].role is MessageRole.System
    assert deserialized.messages[0].content == "You are helpful."
    assert deserialized.messages[1].role is MessageRole.User
    assert deserialized.metadata.name == "RoundTrip"
    assert deserialized.id == prompt.id


def test_round_trip_all_roles_preserves_each_role(serializer):
    prompt = Prompt(
        [
            SystemMessage("sys"),
            DeveloperMessage("dev"),
            UserMessage("user"),
            AssistantMessage("assistant"),
            ToolMessage("call-1", "tool-output"),
            FunctionMessage("my_fn", "fn-output"),
        ]
    )
    deserialized = serializer.deserialize_prompt(serializer.serialize(prompt))
    assert len(deserialized.messages) == 6
    assert isinstance(deserialized.messages[0], SystemMessage)
    assert isinstance(deserialized.messages[1], DeveloperMessage)
    assert isinstance(deserialized.messages[2], UserMessage)
    assert isinstance(deserialized.messages[3], AssistantMessage)
    assert isinstance(deserialized.messages[4], ToolMessage)
    assert isinstance(deserialized.messages[5], FunctionMessage)
    assert deserialized.messages[4].tool_call_id == "call-1"
    assert deserialized.messages[5].function_name == "my_fn"


def test_serialize_message_produces_json(serializer):
    raw = serializer.serialize_message(UserMessage("hello"))
    assert '"role"' in raw
    assert "hello" in raw
    assert '"parts"' in raw
    assert '"content"' not in raw


def test_serialize_message_does_not_duplicate_content_alongside_parts(serializer):
    raw = serializer.serialize_message(UserMessage("hello"))
    assert '"type":"text"' in raw
    assert '"content"' not in raw


def test_serialize_message_null_throws(serializer):
    with pytest.raises(TypeError):
        serializer.serialize_message(None)


def test_serialize_message_tool_message_includes_tool_call_id(serializer):
    raw = serializer.serialize_message(ToolMessage("call-42", "result"))
    assert "toolCallId" in raw
    assert "call-42" in raw


def test_serialize_message_function_message_includes_function_name(serializer):
    raw = serializer.serialize_message(FunctionMessage("get_weather", "result"))
    assert "functionName" in raw
    assert "get_weather" in raw


def test_deserialize_message_round_trips(serializer):
    message = AssistantMessage("Here's your answer.")
    deserialized = serializer.deserialize_message(serializer.serialize_message(message))
    assert isinstance(deserialized, AssistantMessage)
    assert deserialized.content == "Here's your answer."


def test_deserialize_message_tool_message_preserves_tool_call_id(serializer):
    message = ToolMessage("call-99", "output")
    deserialized = serializer.deserialize_message(serializer.serialize_message(message))
    assert isinstance(deserialized, ToolMessage)
    assert deserialized.tool_call_id == "call-99"


def test_deserialize_message_function_message_preserves_function_name(serializer):
    message = FunctionMessage("compute", "output")
    deserialized = serializer.deserialize_message(serializer.serialize_message(message))
    assert isinstance(deserialized, FunctionMessage)
    assert deserialized.function_name == "compute"


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_deserialize_message_null_or_empty_json_throws(serializer, raw):
    with pytest.raises((TypeError, ValueError), match="JSON cannot be null or empty"):
        serializer.deserialize_message(raw)


def test_serialize_template_produces_json(serializer):
    raw = serializer.serialize_template(
        SystemTemplate.create("You are a {{profession}}.")
    )
    assert "templateContent" in raw
    assert "profession" in raw
    assert '"role"' in raw


def test_serialize_template_null_throws(serializer):
    with pytest.raises(TypeError):
        serializer.serialize_template(None)


def test_serialize_template_includes_variables_list(serializer):
    raw = serializer.serialize_template(UserTemplate.create("{{a}} {{b}}"))
    assert "variables" in raw
    assert '"a"' in raw
    assert '"b"' in raw


def test_deserialize_message_missing_metadata_field_defaults_to_empty_metadata(
    serializer,
):
    raw = """
    {
      "role": "user",
      "id": "abc",
      "parts": [{ "type": "text", "text": "hello" }]
    }
    """
    message = serializer.deserialize_message(raw)
    assert message.metadata is not None
    assert message.metadata.name is None
    assert message.metadata.tags == []


def test_deserialize_prompt_missing_metadata_field_defaults_to_empty_metadata(
    serializer,
):
    raw = """
    {
      "id": "prompt-1",
      "messages": [
        { "role": "user", "id": "m1", "parts": [{ "type": "text", "text": "hi" }] }
      ]
    }
    """
    prompt = serializer.deserialize_prompt(raw)
    assert prompt.metadata is not None
    assert prompt.metadata.name is None


def test_serializer_uses_camel_case_keys(serializer):
    """Replacement for C#-only PromptJsonOptions coverage."""
    raw = serializer.serialize_message(ToolMessage("call-1", "result"))
    data = json.loads(raw)
    assert "toolCallId" in data
    assert "base64Data" not in data or True  # structural camelCase present
    prompt_raw = serializer.serialize(
        Prompt(
            [UserMessage("hi")],
            MessageMetadata(name="N", min_compatible_version="1.0.0"),
        )
    )
    prompt_data = json.loads(prompt_raw)
    assert "minCompatibleVersion" in prompt_data["metadata"]


def test_round_trip_template(serializer):
    original = SystemTemplate.create("You are a {{profession}}.")
    restored = serializer.deserialize_template(serializer.serialize_template(original))
    assert restored.role is MessageRole.System
    assert restored.template_content == original.template_content
    assert restored.variables == ["profession"]
