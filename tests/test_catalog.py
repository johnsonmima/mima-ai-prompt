"""Port of CatalogTests.cs."""

import pytest

from mima_ai_prompt import SystemTemplate, SystemTemplates, UserTemplate, UserTemplates
from mima_ai_prompt.roles import MessageRole


def _system_templates():
    return [
        (name, value)
        for name, value in vars(SystemTemplates).items()
        if not name.startswith("_") and isinstance(value, SystemTemplate)
    ]


def _user_templates():
    return [
        (name, value)
        for name, value in vars(UserTemplates).items()
        if not name.startswith("_") and isinstance(value, UserTemplate)
    ]


_SYSTEM = _system_templates()
_USER = _user_templates()


@pytest.mark.parametrize("name,template", _SYSTEM, ids=[n for n, _ in _SYSTEM])
def test_system_templates_property_is_non_null_with_content_and_system_role(
    name, template
):
    assert template is not None
    assert template.template_content and template.template_content.strip()
    assert template.role is MessageRole.System
    assert template.metadata.name and template.metadata.name.strip()


@pytest.mark.parametrize("name,template", _USER, ids=[n for n, _ in _USER])
def test_user_templates_property_is_non_null_with_content_and_user_role(name, template):
    assert template is not None
    assert template.template_content and template.template_content.strip()
    assert template.role is MessageRole.User
    assert template.metadata.name and template.metadata.name.strip()


def test_system_templates_has_at_least_expected_number_of_personas():
    assert len(_SYSTEM) >= 20


def test_user_templates_has_at_least_expected_number_of_templates():
    assert len(_USER) >= 15


def test_configurable_has_profession_tone_max_words_variables():
    assert SystemTemplates.Configurable.variables == ["profession", "tone", "maxWords"]


def test_configurable_renders_with_values_provided():
    message = SystemTemplates.Configurable.render(
        {"profession": "Teacher", "tone": "Friendly", "maxWords": "200"}
    )
    assert "You are a Teacher." in message.content
    assert "Use a Friendly tone." in message.content
    assert "Limit responses to 200 words." in message.content


@pytest.mark.parametrize("name,template", _USER, ids=[n for n, _ in _USER])
def test_user_templates_smoke_render_with_dummy_values_for_all_variables(
    name, template
):
    variables = {v: f"dummy-{v}" for v in template.variables}
    message = template.render(variables)
    assert message is not None
    assert message.content and message.content.strip()
    for variable in template.variables:
        assert f"dummy-{variable}" in message.content


def test_system_templates_have_no_leading_whitespace():
    for name, template in _SYSTEM:
        for line in template.template_content.splitlines():
            if line:
                assert line == line.lstrip(" "), name


def test_user_templates_have_no_leading_whitespace():
    for name, template in _USER:
        for line in template.template_content.splitlines():
            if line:
                assert line == line.lstrip(" "), name


def test_helpful_assistant_has_no_variables():
    assert SystemTemplates.HelpfulAssistant.variables == []


def test_summarize_has_style_and_content_variables():
    assert UserTemplates.Summarize.variables == ["style", "content"]
