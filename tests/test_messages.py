"""Port of MessageTests.cs."""

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    DeveloperMessage,
    FunctionMessage,
    Message,
    MessageMetadata,
    MessageRole,
    PromptValidationException,
    SystemMessage,
    ToolMessage,
    UserMessage,
)


def test_system_message_create_has_correct_role_and_content():
    message = SystemMessage.create("You are helpful.")
    assert message.role is MessageRole.System
    assert message.content == "You are helpful."
    assert message.id


def test_system_message_ctor_with_metadata_and_id_passthrough():
    metadata = MessageMetadata.with_name("sys")
    message = SystemMessage("content", metadata, "fixed-id")
    assert message.metadata is metadata
    assert message.id == "fixed-id"


def test_user_message_create_has_correct_role_and_content():
    message = UserMessage.create("Hello")
    assert message.role is MessageRole.User
    assert message.content == "Hello"


def test_user_message_ctor_works():
    assert UserMessage("Hi there").role is MessageRole.User


def test_assistant_message_create_has_correct_role_and_content():
    message = AssistantMessage.create("Sure, here's the answer.")
    assert message.role is MessageRole.Assistant
    assert message.content == "Sure, here's the answer."


def test_assistant_message_ctor_works():
    assert AssistantMessage("answer").role is MessageRole.Assistant


def test_developer_message_create_has_correct_role_and_content():
    message = DeveloperMessage.create("Respond in Markdown.")
    assert message.role is MessageRole.Developer
    assert message.content == "Respond in Markdown."


def test_developer_message_ctor_works():
    assert DeveloperMessage("dev instructions").role is MessageRole.Developer


def test_tool_message_create_has_correct_role_and_tool_call_id():
    message = ToolMessage.create("call-1", '{ "result": true }')
    assert message.role is MessageRole.Tool
    assert message.tool_call_id == "call-1"
    assert message.content == '{ "result": true }'


def test_tool_message_ctor_works():
    assert ToolMessage("call-2", "output").tool_call_id == "call-2"


@pytest.mark.parametrize("tool_call_id", [None, "", "   "])
def test_tool_message_empty_tool_call_id_throws(tool_call_id):
    with pytest.raises(ValueError, match="Tool call ID cannot be null or empty"):
        ToolMessage(tool_call_id, "content")


def test_function_message_create_has_correct_role_and_function_name():
    message = FunctionMessage.create("get_weather", '{ "temp": 72 }')
    assert message.role is MessageRole.Function
    assert message.function_name == "get_weather"
    assert message.content == '{ "temp": 72 }'


def test_function_message_ctor_works():
    assert FunctionMessage("fn", "content").function_name == "fn"


@pytest.mark.parametrize("function_name", [None, "", "   "])
def test_function_message_empty_function_name_throws(function_name):
    with pytest.raises(ValueError, match="Function name cannot be null or empty"):
        FunctionMessage(function_name, "content")


@pytest.mark.parametrize("content", [None, "", "   "])
def test_message_empty_content_throws(content):
    with pytest.raises(
        PromptValidationException, match="Message content cannot be null or empty"
    ):
        SystemMessage(content)


def test_message_null_role_throws():
    class TestMessage(Message):
        pass

    with pytest.raises(TypeError):
        TestMessage(None, "content")


def test_equals_same_id_and_body_returns_true():
    a = UserMessage("content", id="same-id")
    b = UserMessage("content", id="same-id")
    assert a == b
    assert hash(a) == hash(b)


def test_equals_same_id_different_body_returns_false():
    a = UserMessage("content", id="same-id")
    b = UserMessage("different content", id="same-id")
    assert a != b


def test_equals_different_id_returns_false():
    a = UserMessage("content", id="id-1")
    b = UserMessage("content", id="id-2")
    assert a != b


def test_equals_null_returns_false():
    a = UserMessage("content")
    assert a != None
    assert a != "not a message"


def test_to_string_short_content_returns_full_content():
    assert str(UserMessage("short")) == "[user] short"


def test_to_string_long_content_truncates_to_50_characters():
    long_content = "a" * 100
    assert str(UserMessage(long_content)) == f"[user] {long_content[:50]}"


def test_to_string_exactly_fifty_characters_returns_full_content():
    content = "b" * 50
    assert str(UserMessage(content)) == f"[user] {content}"


def test_metadata_defaults_to_empty_when_not_provided():
    message = UserMessage("content")
    assert message.metadata is not None
    assert message.metadata.name is None


def test_id_generated_automatically_when_not_provided():
    a = UserMessage("content")
    b = UserMessage("content")
    assert a.id != b.id
