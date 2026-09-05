"""Port of EndToEndUsageTests.cs."""

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    Conversation,
    ImagePart,
    LocalizedTemplate,
    MessageRole,
    PromptBuilder,
    PromptSerializer,
    PromptValidationException,
    SystemTemplate,
    TextPart,
    ToolCall,
)


def test_sample_missing_placeholder_validate_then_build_throws():
    template = SystemTemplate.create("You are a {{profession}}. Product: {{product}}.")
    check = template.validate({"profession": "Teacher"})
    assert check.is_valid is False
    assert check.missing_variables == ["product"]
    assert "Missing required variable: 'product'" in check.errors

    with pytest.raises(
        PromptValidationException, match="Missing required variable: 'product'"
    ):
        PromptBuilder.use(template).useWith("profession", "Teacher").add_user(
            "Hello"
        ).build()


def test_sample_localized_template_renders_locale_and_falls_back():
    support = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("en", "You are a support agent for {{product}}. Be concise.")
        .add_locale(
            "fr", "Vous êtes un agent de support pour {{product}}. Soyez concis."
        )
        .with_default("en")
    )
    french = support.render("fr", {"product": "Billing"})
    assert french.role is MessageRole.System
    assert french.content == "Vous êtes un agent de support pour Billing. Soyez concis."

    prompt = (
        PromptBuilder.create()
        .add_message(french)
        .add_user("Pourquoi ai-je été facturé deux fois ?")
        .build()
    )
    assert len(prompt.messages) == 2
    assert "Billing" in prompt.system_message.content
    assert support.has_locale("fr")
    assert "{{product}}" in support.get_content("fr")

    german_fallback = support.render("de", {"product": "Billing"})
    assert german_fallback.content == "You are a support agent for Billing. Be concise."


def test_sample_text_prompt_serializes():
    prompt = (
        PromptBuilder.system("You are a helpful assistant.")
        .add_user("Explain dependency injection.")
        .build()
    )
    assert "dependency injection" in PromptSerializer().serialize(prompt)


def test_sample_vision_url_and_base64():
    vision = (
        PromptBuilder.create()
        .add_system("You are a vision assistant.")
        .add_user_with_image(
            "What objects are in this photo?", "https://example.com/photo.png"
        )
        .build()
    )
    assert "https://example.com/photo.png" in PromptSerializer().serialize(vision)

    inline = (
        PromptBuilder.create()
        .add_user(
            [
                TextPart.create("Describe"),
                ImagePart.from_base64("abc", "image/png", detail="high"),
            ]
        )
        .build()
    )
    assert "abc" in PromptSerializer().serialize(inline)


def test_sample_conversation_to_prompt():
    conversation = (
        Conversation.create("session")
        .with_system("Be brief.")
        .add_user("Hi")
        .add_assistant("Hello")
    )
    assert len(conversation.to_prompt().messages) == 3


def test_sample_tool_follow_up_transcript():
    first = (
        PromptBuilder.create()
        .add_system("Weather agent.")
        .add_user("Weather in NYC?")
        .build()
    )
    assistant = AssistantMessage.create_with_tool_calls(
        [ToolCall.create("call_1", "get_weather", '{"city":"NYC"}')]
    )
    second = (
        PromptBuilder.create()
        .add_system("Weather agent.")
        .add_user("Weather in NYC?")
        .add_message(assistant)
        .add_tool("call_1", '{"temp_f":72}')
        .build()
    )
    assert "call_1" in PromptSerializer().serialize(second)
    restored = PromptSerializer().deserialize_prompt(
        PromptSerializer().serialize(first)
    )
    assert "NYC" in restored.last_user_message.content
