"""Port of PromptModelTests.cs."""

from datetime import datetime, timedelta, timezone

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    Conversation,
    MessageMetadata,
    MessageRole,
    OutputFormat,
    Prompt,
    PromptValidationException,
    PromptVariable,
    SystemMessage,
    TemplateValidationResult,
    ToolMessage,
    UserMessage,
)


def test_ctor_null_messages_throws():
    with pytest.raises(TypeError):
        Prompt(None)


def test_ctor_empty_messages_throws():
    with pytest.raises(PromptValidationException, match="at least one message"):
        Prompt([])


def test_ctor_generates_id_when_not_provided():
    assert Prompt([UserMessage("hi")]).id


def test_ctor_uses_provided_id():
    assert Prompt([UserMessage("hi")], id="fixed-id").id == "fixed-id"


def test_message_count_reflects_message_count():
    assert Prompt([UserMessage("a"), AssistantMessage("b")]).message_count == 2


def test_system_message_returns_first_system_message():
    sys = SystemMessage("sys")
    prompt = Prompt([sys, UserMessage("hi")])
    assert prompt.system_message is sys


def test_system_message_none_exists_returns_null():
    assert Prompt([UserMessage("hi")]).system_message is None


def test_last_user_message_returns_last_user():
    last_user = UserMessage("second")
    prompt = Prompt([UserMessage("first"), AssistantMessage("reply"), last_user])
    assert prompt.last_user_message is last_user


def test_last_user_message_none_exists_returns_null():
    assert Prompt([SystemMessage("sys")]).last_user_message is None


def test_get_messages_filters_by_role():
    prompt = Prompt(
        [
            SystemMessage("sys"),
            UserMessage("u1"),
            AssistantMessage("a1"),
            UserMessage("u2"),
        ]
    )
    assert len(prompt.get_messages(MessageRole.User)) == 2


def test_to_string_includes_count_and_name_or_id():
    prompt = Prompt([UserMessage("hi")], MessageMetadata(name="MyPrompt"))
    assert str(prompt) == "Prompt [1 messages] MyPrompt"


def test_to_string_no_name_uses_id():
    prompt = Prompt([UserMessage("hi")], id="abc123")
    assert str(prompt) == "Prompt [1 messages] abc123"


def test_conversation_create_sets_name_and_id():
    conversation = Conversation.create("Chat")
    assert conversation.name == "Chat"
    assert conversation.id
    assert conversation.message_count == 0
    assert conversation.system_message is None


def test_conversation_with_system_sets_system_message():
    conversation = Conversation.create("Chat").with_system("Be helpful.")
    assert conversation.system_message.content == "Be helpful."


def test_conversation_add_user_adds_user_message():
    conversation = Conversation.create("Chat").add_user("Hi")
    assert sum(1 for m in conversation.messages if m.role is MessageRole.User) == 1


def test_conversation_add_assistant_adds_assistant_message():
    conversation = Conversation.create("Chat").add_user("Hi").add_assistant("Hello")
    assert conversation.message_count == 2


def test_conversation_add_message_adds_any_message():
    tool_message = ToolMessage("call-1", "result")
    conversation = Conversation.create("Chat").add_message(tool_message)
    assert tool_message in conversation.messages


def test_conversation_add_message_null_throws():
    with pytest.raises(TypeError):
        Conversation.create("Chat").add_message(None)


def test_conversation_to_prompt_includes_system_and_messages():
    conversation = (
        Conversation.create("Chat")
        .with_system("Be helpful.")
        .add_user("Hi")
        .add_assistant("Hello!")
    )
    prompt = conversation.to_prompt()
    assert len(prompt.messages) == 3
    assert prompt.messages[0].role is MessageRole.System
    assert prompt.metadata.name == "Chat"


def test_conversation_to_prompt_no_system_excludes_system():
    conversation = Conversation.create("Chat").add_user("Hi")
    prompt = conversation.to_prompt()
    assert len(prompt.messages) == 1
    assert prompt.messages[0].role is MessageRole.User


def test_conversation_created_is_set_on_creation():
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    conversation = Conversation.create("Chat")
    after = datetime.now(timezone.utc) + timedelta(seconds=1)
    assert before <= conversation.created <= after


def test_to_prompt_with_window_count_less_than_messages_returns_last_n():
    conversation = Conversation.create("Chat").with_system("sys")
    for i in range(5):
        conversation.add_user(f"u{i}")
    prompt = conversation.to_prompt_with_window(2)
    assert len(prompt.messages) == 3
    assert prompt.messages[1].content == "u3"
    assert prompt.messages[2].content == "u4"


def test_to_prompt_with_window_count_greater_than_messages_returns_all():
    conversation = (
        Conversation.create("Chat").with_system("sys").add_user("u0").add_user("u1")
    )
    prompt = conversation.to_prompt_with_window(100)
    assert len(prompt.messages) == 3


def test_to_prompt_with_window_zero_count_returns_only_system():
    conversation = (
        Conversation.create("Chat").with_system("sys").add_user("u0").add_user("u1")
    )
    prompt = conversation.to_prompt_with_window(0)
    assert len(prompt.messages) == 1
    assert prompt.messages[0].role is MessageRole.System


def test_to_prompt_with_window_negative_count_treated_as_zero_throws_when_resulting_list_empty():
    conversation = Conversation.create("Chat").add_user("u0").add_user("u1")
    with pytest.raises(PromptValidationException, match="at least one message"):
        conversation.to_prompt_with_window(-5)


def test_to_prompt_with_window_negative_count_with_system_message_returns_only_system():
    conversation = (
        Conversation.create("Chat").with_system("sys").add_user("u0").add_user("u1")
    )
    prompt = conversation.to_prompt_with_window(-5)
    assert len(prompt.messages) == 1
    assert prompt.messages[0].role is MessageRole.System


def test_to_prompt_with_window_no_system_works_without_system():
    conversation = (
        Conversation.create("Chat").add_user("u0").add_user("u1").add_user("u2")
    )
    prompt = conversation.to_prompt_with_window(2)
    assert len(prompt.messages) == 2
    assert prompt.messages[0].content == "u1"
    assert prompt.messages[1].content == "u2"


def test_prompt_variable_required_creates_required_variable():
    variable = PromptVariable.required("topic", "The topic to discuss")
    assert variable.name == "topic"
    assert variable.description == "The topic to discuss"
    assert variable.is_required is True
    assert variable.default_value is None


def test_prompt_variable_optional_creates_optional_variable_with_default():
    variable = PromptVariable.optional("tone", "friendly", "The tone to use")
    assert variable.is_required is False
    assert variable.default_value == "friendly"
    assert variable.description == "The tone to use"


@pytest.mark.parametrize("name", [None, "", "   "])
def test_prompt_variable_empty_name_throws(name):
    with pytest.raises(ValueError, match="Variable name cannot be null or empty"):
        PromptVariable(name)


def test_prompt_variable_examples_defaults_to_empty():
    assert PromptVariable.required("name").examples == []


def test_prompt_variable_examples_can_be_provided():
    variable = PromptVariable("name", examples=["Alice", "Bob"])
    assert variable.examples == ["Alice", "Bob"]


def test_prompt_variable_type_hint_can_be_set():
    assert PromptVariable("count", type_hint="int").type_hint == "int"


def test_template_validation_result_success_is_valid():
    result = TemplateValidationResult.success()
    assert result.is_valid
    assert result.missing_variables == []
    assert result.errors == []


def test_template_validation_result_failure_lists_missing_variables_and_errors():
    result = TemplateValidationResult.failure(["name", "topic"])
    assert result.is_valid is False
    assert set(result.missing_variables) == {"name", "topic"}
    assert len(result.errors) == 2
    assert "name" in result.errors[0]


def test_template_validation_result_from_errors_sets_errors_only():
    result = TemplateValidationResult.from_errors(["Some general error."])
    assert result.is_valid is False
    assert result.errors == ["Some general error."]
    assert result.missing_variables == []


def test_template_validation_result_ctor_defaults_to_empty_collections():
    result = TemplateValidationResult(True)
    assert result.missing_variables == []
    assert result.extra_variables == []
    assert result.errors == []


def test_output_format_json_has_correct_type_and_instructions():
    fmt = OutputFormat.json()
    assert fmt.type == OutputFormat.JSON
    assert "valid JSON" in fmt.instructions
    assert fmt.schema is None


def test_output_format_json_with_schema_sets_schema():
    fmt = OutputFormat.json('{ "type": "object" }')
    assert fmt.schema == '{ "type": "object" }'


def test_output_format_markdown_has_correct_type():
    fmt = OutputFormat.markdown()
    assert fmt.type == OutputFormat.MARKDOWN
    assert "Markdown" in fmt.instructions


def test_output_format_plain_text_has_correct_type():
    fmt = OutputFormat.plain_text()
    assert fmt.type == OutputFormat.PLAIN_TEXT
    assert "plain text" in fmt.instructions


def test_output_format_bullet_points_has_correct_type():
    fmt = OutputFormat.bullet_points()
    assert fmt.type == OutputFormat.BULLETS
    assert "bullet points" in fmt.instructions


def test_output_format_steps_has_correct_type():
    fmt = OutputFormat.steps()
    assert fmt.type == OutputFormat.STEPS
    assert "numbered steps" in fmt.instructions


def test_output_format_json_with_schema_includes_schema_in_instructions():
    fmt = OutputFormat.json_with_schema('{ "name": "string" }')
    assert fmt.type == OutputFormat.JSON
    assert fmt.schema == '{ "name": "string" }'
    assert '{ "name": "string" }' in fmt.instructions


def test_output_format_custom_uses_provided_type_and_instructions():
    fmt = OutputFormat.custom("csv", "Respond with CSV only.")
    assert fmt.type == "csv"
    assert fmt.instructions == "Respond with CSV only."
    assert fmt.schema is None


def test_output_format_yaml_has_correct_type_and_instructions():
    fmt = OutputFormat.yaml()
    assert fmt.type == OutputFormat.YAML
    assert "valid YAML" in fmt.instructions
    assert fmt.schema is None


def test_output_format_yaml_with_schema_sets_schema():
    fmt = OutputFormat.yaml("name: string")
    assert fmt.type == OutputFormat.YAML
    assert fmt.schema == "name: string"


def test_output_format_yaml_with_schema_includes_schema_in_instructions():
    fmt = OutputFormat.yaml_with_schema("name: string\nage: number")
    assert fmt.type == OutputFormat.YAML
    assert "name: string" in fmt.schema
    assert "name: string" in fmt.instructions
    assert "valid YAML" in fmt.instructions
