"""Port of TemplateTests.cs."""

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    AssistantTemplate,
    DeveloperMessage,
    DeveloperTemplate,
    MessageMetadata,
    MessageTemplate,
    PromptValidationException,
    PromptVariable,
    SystemMessage,
    SystemTemplate,
    UserMessage,
    UserTemplate,
)
from mima_ai_prompt.roles import MessageRole


def test_system_template_create_content_only_works():
    template = SystemTemplate.create("You are a {{profession}}.")
    assert template.role is MessageRole.System
    assert template.template_content == "You are a {{profession}}."
    assert template.variables == ["profession"]


def test_system_template_create_named_variant_sets_metadata_name():
    template = SystemTemplate.create("MyTemplate", "Content here.")
    assert template.metadata.name == "MyTemplate"


def test_system_template_render_produces_system_message():
    template = SystemTemplate.create("You are a {{profession}}.")
    message = template.render({"profession": "teacher"})
    assert isinstance(message, SystemMessage)
    assert message.content == "You are a teacher."


def test_user_template_create_content_only_works():
    assert UserTemplate.create("Hello {{name}}").role is MessageRole.User


def test_user_template_create_named_variant_works():
    assert (
        UserTemplate.create("MyUserTemplate", "Hi {{name}}").metadata.name
        == "MyUserTemplate"
    )


def test_user_template_render_produces_user_message():
    message = UserTemplate.create("Hi {{name}}").render({"name": "Bob"})
    assert isinstance(message, UserMessage)
    assert message.content == "Hi Bob"


def test_assistant_template_create_content_only_works():
    assert AssistantTemplate.create("Answer: {{answer}}").role is MessageRole.Assistant


def test_assistant_template_create_named_variant_works():
    assert (
        AssistantTemplate.create("MyAssistant", "Answer: {{answer}}").metadata.name
        == "MyAssistant"
    )


def test_assistant_template_render_produces_assistant_message():
    message = AssistantTemplate.create("Answer: {{answer}}").render({"answer": "42"})
    assert isinstance(message, AssistantMessage)
    assert message.content == "Answer: 42"


def test_developer_template_create_content_only_works():
    assert DeveloperTemplate.create("Use {{language}}.").role is MessageRole.Developer


def test_developer_template_create_named_variant_works():
    assert (
        DeveloperTemplate.create("MyDev", "Use {{language}}.").metadata.name == "MyDev"
    )


def test_developer_template_render_produces_developer_message():
    message = DeveloperTemplate.create("Use {{language}}.").render({"language": "C#"})
    assert isinstance(message, DeveloperMessage)
    assert message.content == "Use C#."


def test_variables_discovers_profession_tone_and_max_words():
    template = SystemTemplate.create(
        "You are a {{profession}}. Use a {{tone}} tone. Limit responses to {{maxWords}} words."
    )
    assert template.variables == ["profession", "tone", "maxWords"]


def test_variables_discovers_multiple_distinct_variables():
    template = SystemTemplate.create("{{a}} and {{b}} and {{a}} again")
    assert set(template.variables) == {"a", "b"}


def test_variables_no_placeholders_returns_empty():
    assert SystemTemplate.create("No variables here.").variables == []


def test_validate_missing_variable_returns_invalid_with_errors():
    result = SystemTemplate.create("Hi {{name}}").validate({})
    assert result.is_valid is False
    assert "name" in result.missing_variables
    assert len(result.errors) == 1


def test_validate_profession_without_product_reports_product_missing():
    check = SystemTemplate.create(
        "You are a {{profession}}. Product: {{product}}."
    ).validate({"profession": "Teacher"})
    assert check.is_valid is False
    assert check.missing_variables == ["product"]
    assert check.errors == ["Missing required variable: 'product'"]


def test_validate_null_variable_value_treated_as_missing():
    result = SystemTemplate.create("Hi {{name}}").validate({"name": None})
    assert result.is_valid is False
    assert "name" in result.missing_variables


def test_validate_extra_variable_is_invalid():
    result = SystemTemplate.create("Hi {{name}}").validate(
        {"name": "Bob", "extra": "value"}
    )
    assert result.is_valid is False
    assert result.extra_variables == ["extra"]


def test_validate_all_variables_provided_succeeds():
    result = SystemTemplate.create("Hi {{name}}").validate({"name": "Bob"})
    assert result.is_valid is True
    assert result.missing_variables == []


def test_render_missing_variables_throws():
    with pytest.raises(PromptValidationException):
        SystemTemplate.create("Hi {{name}}").render({})


def test_render_object_overload_uses_properties_as_variables():
    class Values:
        def __init__(self):
            self.profession = "Teacher"
            self.tone = "Friendly"

    message = SystemTemplate.create("You are a {{profession}}. Tone: {{tone}}.").render(
        Values()
    )
    assert message.content == "You are a Teacher. Tone: Friendly."


def test_render_object_overload_with_dictionary_object_uses_directly():
    variables: object = {"name": "Dict"}
    message = UserTemplate.create("Hi {{name}}").render(variables)
    assert message.content == "Hi Dict"


@pytest.mark.parametrize("content", [None, "", "   "])
def test_ctor_empty_content_throws(content):
    with pytest.raises(
        PromptValidationException, match="Template content cannot be null or empty"
    ):
        SystemTemplate.create(content)


def test_ctor_null_role_throws():
    class TestTemplate(MessageTemplate):
        def _create_message(self, rendered_content: str):
            return UserMessage(rendered_content)

    with pytest.raises(TypeError):
        TestTemplate(None, "content")


def test_create_content_plus_metadata():
    metadata = MessageMetadata.with_name("from-meta")
    template = SystemTemplate.create("Hello {{name}}", metadata)
    assert template.template_content == "Hello {{name}}"
    assert template.metadata.name == "from-meta"


def test_optional_variable_def_uses_default_when_omitted():
    template = SystemTemplate.create(
        "Tone: {{tone}}.",
        variable_defs=[PromptVariable.optional("tone", "calm")],
    )
    assert template.validate({}).is_valid
    assert template.render({}).content == "Tone: calm."


def test_required_variable_def_not_in_text_still_required():
    template = SystemTemplate.create(
        "static",
        variable_defs=[PromptVariable.required("topic")],
    )
    assert template.variables == ["topic"]
    result = template.validate({})
    assert result.is_valid is False
    assert result.missing_variables == ["topic"]
