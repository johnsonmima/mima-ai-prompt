"""Port of LocalizationTests.cs."""

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    DeveloperMessage,
    LocalizedTemplate,
    MessageMetadata,
    MessageRole,
)


def test_create_sets_role_and_default_metadata():
    template = LocalizedTemplate.create(MessageRole.System)
    assert template.role is MessageRole.System
    assert template.metadata is not None
    assert template.default_locale == "en"
    assert template.available_locales == []


def test_create_null_role_throws():
    with pytest.raises(TypeError):
        LocalizedTemplate.create(None)


def test_create_with_metadata_uses_provided_metadata():
    metadata = MessageMetadata.with_name("Greeting")
    template = LocalizedTemplate.create(MessageRole.System, metadata)
    assert template.metadata.name == "Greeting"


def test_add_locale_adds_content_for_locale():
    template = LocalizedTemplate.create(MessageRole.System).add_locale(
        "en", "You are a helpful assistant."
    )
    assert "en" in template.available_locales
    assert template.has_locale("en")


@pytest.mark.parametrize("locale", [None, "", "   "])
def test_add_locale_empty_locale_throws(locale):
    template = LocalizedTemplate.create(MessageRole.System)
    with pytest.raises(ValueError, match="Locale cannot be empty"):
        template.add_locale(locale, "content")


@pytest.mark.parametrize("content", [None, "", "   "])
def test_add_locale_empty_content_throws(content):
    template = LocalizedTemplate.create(MessageRole.System)
    with pytest.raises(ValueError, match="Content cannot be empty"):
        template.add_locale("en", content)


def test_with_default_sets_default_locale():
    template = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("fr", "Bonjour")
        .with_default("fr")
    )
    assert template.default_locale == "fr"


def test_with_metadata_updates_metadata():
    template = LocalizedTemplate.create(MessageRole.System).with_metadata(
        MessageMetadata.with_name("Updated")
    )
    assert template.metadata.name == "Updated"


def test_get_content_existing_locale_returns_content():
    template = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("en", "Hello")
        .add_locale("fr", "Bonjour")
    )
    assert template.get_content("fr") == "Bonjour"


def test_get_content_missing_locale_falls_back_to_default():
    template = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("en", "Hello")
        .with_default("en")
    )
    assert template.get_content("de") == "Hello"


def test_get_content_no_default_and_no_match_returns_first_available():
    template = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("fr", "Bonjour")
        .with_default("nonexistent-default")
    )
    assert template.get_content("de") == "Bonjour"


def test_get_content_no_locales_added_throws():
    template = LocalizedTemplate.create(MessageRole.System)
    with pytest.raises(RuntimeError, match="No localized content has been added"):
        template.get_content("en")


def test_render_system_role_produces_system_message():
    template = LocalizedTemplate.create(MessageRole.System).add_locale(
        "en", "You are a {{profession}}."
    )
    message = template.render("en", {"profession": "teacher"})
    assert message.role is MessageRole.System
    assert message.content == "You are a teacher."


def test_render_user_role_produces_user_message():
    template = LocalizedTemplate.create(MessageRole.User).add_locale(
        "en", "Hello {{name}}"
    )
    message = template.render("en", {"name": "Bob"})
    assert message.role is MessageRole.User
    assert message.content == "Hello Bob"


def test_render_assistant_role_produces_assistant_message():
    template = LocalizedTemplate.create(MessageRole.Assistant).add_locale(
        "en", "Answer: {{value}}"
    )
    message = template.render("en", {"value": "42"})
    assert isinstance(message, AssistantMessage)
    assert message.role is MessageRole.Assistant
    assert message.content == "Answer: 42"


def test_render_developer_role_produces_developer_message():
    template = LocalizedTemplate.create(MessageRole.Developer).add_locale(
        "en", "Rule: {{text}}"
    )
    message = template.render("en", {"text": "claim"})
    assert isinstance(message, DeveloperMessage)
    assert message.content == "Rule: claim"


def test_has_locale_unknown_locale_returns_false():
    template = LocalizedTemplate.create(MessageRole.System).add_locale("en", "Hello")
    assert template.has_locale("fr") is False


def test_add_locale_case_insensitive_lookup():
    template = LocalizedTemplate.create(MessageRole.System).add_locale("EN", "Hello")
    assert template.has_locale("en") is True


def test_add_locale_updating_existing_locale_overwrites_content():
    template = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("en", "First")
        .add_locale("en", "Second")
    )
    assert template.get_content("en") == "Second"
