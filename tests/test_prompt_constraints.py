"""Port of PromptConstraintsTests.cs."""

from mima_ai_prompt import OutputFormat, PromptBuilder, PromptConstraints
from mima_ai_prompt.roles import MessageRole


def test_create_returns_empty_constraints():
    constraints = PromptConstraints.create()
    assert constraints.max_word_count is None
    assert constraints.min_word_count is None
    assert constraints.format is None
    assert constraints.must_do == []
    assert constraints.must_not == []


def test_max_words_sets_max_word_count():
    assert PromptConstraints.create().max_words(200).max_word_count == 200


def test_min_words_sets_min_word_count():
    assert PromptConstraints.create().min_words(50).min_word_count == 50


def test_no_emojis_adds_negative_constraint():
    assert PromptConstraints.create().no_emojis().must_not == ["Do not use emojis."]


def test_no_tables_adds_negative_constraint():
    assert "Do not use tables." in PromptConstraints.create().no_tables().must_not


def test_no_code_adds_negative_constraint():
    assert (
        "Do not include code blocks." in PromptConstraints.create().no_code().must_not
    )


def test_no_links_adds_negative_constraint():
    assert (
        "Do not include URLs or links."
        in PromptConstraints.create().no_links().must_not
    )


def test_must_include_adds_positive_constraint():
    assert "Conclusion" in PromptConstraints.create().must_include("Conclusion").must_do


def test_must_avoid_adds_negative_constraint_with_prefix():
    assert "Avoid: jargon" in PromptConstraints.create().must_avoid("jargon").must_not


def test_with_format_sets_format():
    fmt = OutputFormat.json()
    assert PromptConstraints.create().with_format(fmt).format is fmt


def test_must_adds_custom_positive_constraint():
    assert "Be polite" in PromptConstraints.create().must("Be polite").must_do


def test_not_adds_custom_negative_constraint():
    assert "Be rude" in PromptConstraints.create().not_("Be rude").must_not


def test_render_empty_constraints_returns_empty_string():
    assert PromptConstraints.create().render() == ""


def test_render_max_words_includes_limit_line():
    assert (
        "Limit your response to 200 words maximum."
        in PromptConstraints.create().max_words(200).render()
    )


def test_render_min_words_includes_minimum_line():
    assert (
        "Your response must be at least 50 words."
        in PromptConstraints.create().min_words(50).render()
    )


def test_render_format_includes_format_instructions():
    assert (
        "Markdown"
        in PromptConstraints.create().with_format(OutputFormat.markdown()).render()
    )


def test_render_positive_constraints_includes_requirements_section():
    rendered = (
        PromptConstraints.create()
        .must_include("Conclusion")
        .must_include("Summary")
        .render()
    )
    assert "Requirements:" in rendered
    assert "- Conclusion" in rendered
    assert "- Summary" in rendered


def test_render_negative_constraints_includes_restrictions_section():
    rendered = PromptConstraints.create().no_emojis().no_tables().render()
    assert "Restrictions:" in rendered
    assert "- Do not use emojis." in rendered
    assert "- Do not use tables." in rendered


def test_render_full_constraints_includes_all_sections():
    rendered = (
        PromptConstraints.create()
        .max_words(200)
        .min_words(10)
        .with_format(OutputFormat.json())
        .must_include("Conclusion")
        .must("Be concise")
        .no_emojis()
        .must_avoid("jargon")
        .not_("Be rude")
        .render()
    )
    assert "200 words maximum" in rendered
    assert "at least 10 words" in rendered
    assert "valid JSON" in rendered
    assert "Requirements:" in rendered
    assert "- Conclusion" in rendered
    assert "- Be concise" in rendered
    assert "Restrictions:" in rendered
    assert "- Do not use emojis." in rendered
    assert "- Avoid: jargon" in rendered
    assert "- Be rude" in rendered


def test_fluent_methods_are_chainable():
    constraints = (
        PromptConstraints.create()
        .max_words(100)
        .min_words(10)
        .no_emojis()
        .no_tables()
        .no_code()
        .no_links()
        .must_include("a")
        .must_avoid("b")
        .with_format(OutputFormat.plain_text())
        .must("c")
        .not_("d")
    )
    assert constraints is not None
    assert len(constraints.must_do) == 2
    assert len(constraints.must_not) == 6


def test_builder_attaches_constraints_as_developer_message():
    prompt = (
        PromptBuilder.create()
        .add_user("hi")
        .with_constraints(PromptConstraints.create().no_emojis())
        .build()
    )
    assert prompt.messages[0].role is MessageRole.User
    assert prompt.messages[1].role is MessageRole.Developer
    assert "Do not use emojis." in prompt.messages[1].content
