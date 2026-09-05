from mima_ai_prompt import (
    PromptBuilder,
    PromptSerializer,
    PromptValidator,
    SystemTemplate,
    SystemTemplates,
)


def test_quick_prompt_serializes_parts_not_content_field():
    prompt = PromptBuilder.quick("You are helpful.", "Hello")
    raw = PromptSerializer().serialize(prompt)
    assert '"parts"' in raw
    assert '"role":"system"' in raw
    assert '"role":"user"' in raw
    # content is in-memory only
    assert '"content"' not in raw or '"content":' not in raw.replace(
        '"templateContent"', ""
    )


def test_template_missing_variable_validate_and_build():
    template = SystemTemplate.create("You are a {{profession}}. Product: {{product}}.")
    check = template.validate({"profession": "Teacher"})
    assert check.is_valid is False
    assert check.missing_variables == ["product"]
    assert check.errors == ["Missing required variable: 'product'"]

    try:
        (
            PromptBuilder.use(template)
            .useWith("profession", "Teacher")
            .add_user("Hello")
            .build()
        )
        assert False, "expected PromptValidationException"
    except Exception as exc:
        assert "product" in str(exc)


def test_configurable_catalog_renders():
    prompt = (
        PromptBuilder.use(SystemTemplates.Configurable)
        .useWith("profession", "Teacher")
        .useWith("tone", "Friendly")
        .useWith("maxWords", "200")
        .add_user("Explain generics")
        .build()
    )
    assert "Teacher" in prompt.messages[0].content
    assert prompt.last_user_message.content == "Explain generics"
    report = PromptValidator().validate(prompt)
    assert report.is_valid


def test_round_trip_serializer():
    prompt = PromptBuilder.system("sys").add_user("hi").with_name("Demo").build()
    serializer = PromptSerializer()
    restored = serializer.deserialize_prompt(serializer.serialize(prompt))
    assert restored.message_count == 2
    assert restored.metadata.name == "Demo"
    assert restored.messages[0].content == "sys"
