"""Port of PromptBuilderTests.cs."""

import pytest

from mima_ai_prompt import (
    FunctionMessage,
    MessageMetadata,
    MessageRole,
    PromptBuilder,
    PromptValidationException,
    SystemTemplate,
    ToolMessage,
    UserMessage,
    UserTemplate,
)


def test_system_creates_builder_with_system_message():
    prompt = PromptBuilder.system("You are helpful.").build()
    assert len(prompt.messages) == 1
    assert prompt.messages[0].role is MessageRole.System


def test_use_template_renders_on_build():
    template = SystemTemplate.create("You are a {{profession}}.")
    prompt = PromptBuilder.use(template).useWith("profession", "teacher").build()
    assert prompt.messages[0].content == "You are a teacher."
    assert prompt.messages[0].role is MessageRole.System


def test_use_template_null_throws():
    with pytest.raises(TypeError):
        PromptBuilder.use(None)


def test_use_message_adds_message():
    message = UserMessage("Hi")
    prompt = PromptBuilder.use(message).build()
    assert prompt.messages[0] is message


def test_create_returns_empty_builder():
    assert PromptBuilder.create() is not None


def test_add_system_adds_system_message():
    prompt = PromptBuilder.create().add_system("sys").build()
    assert prompt.messages[0].role is MessageRole.System
    assert prompt.messages[0].content == "sys"


def test_add_developer_adds_developer_message():
    prompt = PromptBuilder.create().add_developer("dev").build()
    assert prompt.messages[0].role is MessageRole.Developer


def test_add_user_adds_user_message():
    prompt = PromptBuilder.create().add_user("hello").build()
    assert prompt.messages[0].role is MessageRole.User


def test_add_assistant_adds_assistant_message():
    prompt = PromptBuilder.create().add_user("hi").add_assistant("hello").build()
    assert prompt.messages[1].role is MessageRole.Assistant


def test_add_tool_adds_tool_message():
    prompt = PromptBuilder.create().add_user("hi").add_tool("call-1", "result").build()
    assert prompt.messages[1].role is MessageRole.Tool
    assert isinstance(prompt.messages[1], ToolMessage)
    assert prompt.messages[1].tool_call_id == "call-1"


def test_add_function_adds_function_message():
    prompt = PromptBuilder.create().add_user("hi").add_function("fn", "result").build()
    assert prompt.messages[1].role is MessageRole.Function
    assert isinstance(prompt.messages[1], FunctionMessage)
    assert prompt.messages[1].function_name == "fn"


def test_add_message_adds_given_message():
    message = UserMessage("custom")
    prompt = PromptBuilder.create().add_message(message).build()
    assert prompt.messages[0] is message


def test_add_message_null_throws():
    with pytest.raises(TypeError):
        PromptBuilder.create().add_message(None)


def test_add_template_renders_on_build():
    template = UserTemplate.create("Hello {{name}}")
    prompt = (
        PromptBuilder.create()
        .add_system("sys")
        .add_template(template)
        .useWith("name", "World")
        .build()
    )
    assert len(prompt.messages) == 2
    assert prompt.messages[0].content == "sys"
    assert prompt.messages[1].content == "Hello World"


def test_add_template_null_throws():
    with pytest.raises(TypeError):
        PromptBuilder.create().add_template(None)


def test_with_null_value_throws():
    with pytest.raises(TypeError):
        PromptBuilder.create().useWith("name", None)


@pytest.mark.parametrize("name", [None, "", "   "])
def test_with_empty_name_throws(name):
    with pytest.raises(ValueError, match="Variable name cannot be null or empty"):
        PromptBuilder.create().useWith(name, "value")


def test_with_metadata_sets_metadata_on_prompt():
    metadata = MessageMetadata.with_name("MyPrompt")
    prompt = PromptBuilder.create().add_user("hi").with_metadata(metadata).build()
    assert prompt.metadata is metadata


def test_with_name_sets_name_metadata():
    prompt = PromptBuilder.create().add_user("hi").with_name("Named").build()
    assert prompt.metadata.name == "Named"


def test_add_example_adds_user_and_assistant_pair():
    prompt = (
        PromptBuilder.create()
        .add_example("What is DI?", "It's a design pattern.")
        .build()
    )
    assert len(prompt.messages) == 2
    assert prompt.messages[0].role is MessageRole.User
    assert prompt.messages[1].role is MessageRole.Assistant


def test_add_history_adds_alternating_messages():
    history = [("Hi", "Hello!"), ("How are you?", "I'm good.")]
    prompt = PromptBuilder.create().add_history(history).build()
    assert len(prompt.messages) == 4
    assert prompt.messages[0].role is MessageRole.User
    assert prompt.messages[1].role is MessageRole.Assistant
    assert prompt.messages[2].role is MessageRole.User
    assert prompt.messages[3].role is MessageRole.Assistant


def test_build_with_variables_renders_template():
    template = SystemTemplate.create("Hi {{name}}")
    prompt = (
        PromptBuilder.use(template).useWith("name", "Bob").add_user("question").build()
    )
    assert len(prompt.messages) == 2
    assert prompt.messages[0].content == "Hi Bob"


def test_build_template_with_no_variables_renders_directly():
    template = SystemTemplate.create("Static content, no vars.")
    prompt = PromptBuilder.use(template).add_user("hi").build()
    assert prompt.messages[0].content == "Static content, no vars."


def test_build_template_with_missing_variables_throws():
    template = SystemTemplate.create("Hi {{name}}")
    with pytest.raises(
        PromptValidationException, match="Missing required variable: 'name'"
    ):
        PromptBuilder.use(template).add_user("hi").build()


def test_build_partial_with_missing_product_throws():
    template = SystemTemplate.create("You are a {{profession}}. Product: {{product}}.")
    with pytest.raises(
        PromptValidationException, match="Missing required variable: 'product'"
    ):
        PromptBuilder.use(template).useWith("profession", "Teacher").add_user(
            "Hello"
        ).build()


def test_quick_creates_system_and_user_prompt():
    prompt = PromptBuilder.quick("You are helpful.", "Explain DI.")
    assert len(prompt.messages) == 2
    assert prompt.messages[0].role is MessageRole.System
    assert prompt.messages[1].role is MessageRole.User


def test_user_only_creates_user_only_prompt():
    prompt = PromptBuilder.user_only("Explain DI.")
    assert len(prompt.messages) == 1
    assert prompt.messages[0].role is MessageRole.User


def test_add_user_string_keeps_name():
    prompt = PromptBuilder.create().add_user("hello", name="alice").build()
    assert prompt.messages[0].name == "alice"


def test_unused_template_variable_throws():
    template = SystemTemplate.create("Hi {{name}}")
    with pytest.raises(PromptValidationException, match="Unused variable"):
        PromptBuilder.use(template).useWith("name", "Ada").useWith("extra", "x").build()
