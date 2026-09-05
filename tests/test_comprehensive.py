"""Comprehensive behavioral tests for the public prompt-composition API."""

from datetime import datetime
import inspect
import json

import pytest

from mima_ai_prompt import (
    AssistantMessage,
    AssistantTemplate,
    Conversation,
    DeveloperMessage,
    DeveloperTemplate,
    FunctionMessage,
    ImagePart,
    LocalizedTemplate,
    Message,
    MessageAnnotation,
    MessageMetadata,
    MessageRole,
    OutputFormat,
    Prompt,
    PromptBuilder,
    PromptConstraints,
    PromptSerializer,
    PromptValidationException,
    PromptValidationReport,
    PromptValidator,
    PromptVariable,
    PromptVersion,
    PromptVersionHistory,
    SystemMessage,
    SystemTemplate,
    SystemTemplates,
    TemplateValidationResult,
    TextPart,
    ToolCall,
    ToolMessage,
    UserMessage,
    UserTemplate,
    UserTemplates,
    VersionedPromptAsset,
)


def test_roles_parse_compare_and_enumerate():
    assert str(MessageRole.System) == "system"
    assert repr(MessageRole.User) == "MessageRole('user')"
    assert MessageRole.parse(" USER ") is MessageRole.User
    assert MessageRole.try_parse("bad") is None
    assert MessageRole.try_parse(None) is None
    assert len(MessageRole.all()) == 6
    assert len(set(MessageRole.all())) == 6
    assert MessageRole("user", 9, "custom") == MessageRole.User
    assert MessageRole.User != object()
    with pytest.raises(ValueError):
        MessageRole.parse("")
    with pytest.raises(ValueError, match="Unknown"):
        MessageRole.parse("manager")


def test_content_parts_and_image_validation():
    text = TextPart.create("hello")
    assert text.type == "text" and text.text == "hello"
    assert isinstance(text, object)
    with pytest.raises(TypeError):
        TextPart(None)

    remote = ImagePart.from_url("https://example.test/a.png", "high")
    inline = ImagePart.from_base64("YWJj", "image/png", "low")
    assert (remote.url, remote.detail, remote.type) == (
        "https://example.test/a.png",
        "high",
        "image",
    )
    assert (inline.base64_data, inline.media_type) == ("YWJj", "image/png")
    with pytest.raises(TypeError):
        ImagePart.from_url(None)
    with pytest.raises(ValueError):
        ImagePart()
    with pytest.raises(ValueError):
        ImagePart.from_base64("abc", "")


def test_messages_factories_parts_identity_and_validation():
    metadata = MessageMetadata.with_name("sample")
    annotation = MessageAnnotation.internal_ref("doc")
    system = SystemMessage.create([TextPart("rules")], metadata, "s1", "sys", [annotation])
    developer = DeveloperMessage.create("context", metadata, "d1")
    user = UserMessage.create(
        [ImagePart.from_url("https://example.test/image")],
        metadata,
        "person",
        "u1",
        [annotation],
    )
    assistant = AssistantMessage.create([TextPart("answer")], metadata)

    assert system.name == "sys"
    assert developer.role is MessageRole.Developer
    assert user.content == "" and user.name == "person"
    assert assistant.content == "answer"
    assert str(user) == "[user] [1 part(s)]"
    assert str(SystemMessage("x" * 60)) == "[system] " + "x" * 50
    assert Message(MessageRole.User, "x", id="same") != Message(
        MessageRole.User, "y", id="same"
    )
    assert len({Message(MessageRole.User, "x", id="same")}) == 1
    assert Message(MessageRole.User, "caption", [ImagePart.from_url("x")]).content == (
        "caption"
    )
    with pytest.raises(TypeError):
        Message(None, "x")
    with pytest.raises(PromptValidationException):
        UserMessage("")


def test_assistant_tool_refusal_tool_and_function_messages():
    call = ToolCall.create(" call ", " lookup ", '{"q": 1}')
    tool_assistant = AssistantMessage.create_with_tool_calls([call])
    refusal = AssistantMessage.create_refusal("  cannot comply  ")
    detailed = AssistantMessage.create_detailed(
        content="done", name="worker", annotations=[MessageAnnotation.file_citation("f1")]
    )
    assert tool_assistant.tool_calls == [call] and tool_assistant.content == ""
    assert refusal.refusal == "cannot comply"
    assert detailed.name == "worker"
    assert ToolMessage.create("call", "result").tool_call_id == "call"
    assert FunctionMessage.create("legacy", "result").function_name == "legacy"
    with pytest.raises(PromptValidationException):
        AssistantMessage()
    with pytest.raises(ValueError):
        ToolMessage("", "result")
    with pytest.raises(ValueError):
        FunctionMessage("", "result")
    with pytest.raises(ValueError):
        ToolCall("", "name")
    with pytest.raises(ValueError):
        ToolCall("id", "")
    assert ToolCall("id", "name", "").arguments_json == "{}"


@pytest.mark.parametrize(
    ("template_type", "expected_type"),
    [
        (SystemTemplate, SystemMessage),
        (UserTemplate, UserMessage),
        (AssistantTemplate, AssistantMessage),
        (DeveloperTemplate, DeveloperMessage),
    ],
)
def test_template_types_render_and_named_overloads(template_type, expected_type):
    named = template_type.create("Named", "Hello {{name}}")
    result = named.render({"name": "Ada"})
    assert isinstance(result, expected_type)
    assert result.content == "Hello Ada"
    assert named.metadata.name == "Named"
    direct = template_type.create("Static", MessageMetadata.with_name("meta"))
    assert direct.variables == []
    assert direct.render({}).content == "Static"


def test_template_variables_object_render_validation_and_errors():
    template = UserTemplate.create("{{first}} {{first}} {{second}}")

    class Values:
        def __init__(self):
            self.first = "A"
            self.second = "B"
            self.ignored = None
            self._private = "hidden"

    assert template.variables == ["first", "second"]
    assert template.variables is not template.variables
    assert template.render(Values()).content == "A A B"
    valid = template.validate({"first": "A", "second": "B"})
    assert valid.is_valid
    extra = template.validate({"first": "A", "second": "B", "extra": "x"})
    assert extra.is_valid is False
    missing = template.validate({"first": "A", "extra": "x"})
    assert missing.extra_variables == ["extra"]
    with pytest.raises(PromptValidationException):
        template.render({"first": "A"})
    with pytest.raises(PromptValidationException):
        SystemTemplate(None)
    with pytest.raises(PromptValidationException):
        SystemTemplate(" ")


def test_builder_all_message_paths_history_examples_and_response_format():
    fmt = OutputFormat.json_with_schema('{"type":"object"}')
    call = ToolCall("c1", "lookup")
    prompt = (
        PromptBuilder.create()
        .add_system([TextPart("system")])
        .add_developer([TextPart("developer")])
        .add_user([TextPart("user")], name="named")
        .add_user_with_image("look", "https://example.test/x", "viewer")
        .add_assistant([TextPart("assistant")])
        .add_assistant_tool_calls([call], "calling")
        .add_tool("c1", "result")
        .add_function("legacy", "value")
        .add_message(UserMessage("extra"))
        .add_example("example question", "example answer")
        .add_history([("history question", "history answer")])
        .with_metadata(MessageMetadata.with_name("before"))
        .with_name("Built")
        .with_response_format(fmt)
        .build()
    )
    assert prompt.message_count == 13
    assert prompt.metadata.name == "Built"
    assert prompt.response_format is fmt
    assert prompt.messages[2].name == "named"
    assert prompt.messages[3].name == "viewer"
    assert len(prompt.messages[3].parts) == 2

    for role in (
        MessageRole.System,
        MessageRole.Developer,
        MessageRole.User,
        MessageRole.Assistant,
    ):
        assert PromptBuilder.create().add(role, "x").build().messages[0].role == role
    with pytest.raises(ValueError):
        PromptBuilder.create().add(MessageRole.Tool, "x")
    with pytest.raises(ValueError):
        PromptBuilder.create().add(MessageRole("custom", 9, ""), "x")


def test_builder_templates_aliases_shortcuts_and_invalid_arguments():
    template = SystemTemplate.create("Hello {{name}}")
    prompt = (
        PromptBuilder.use(template)
        .with_var("name", "Ada")
        .add_user("Hi")
        .build()
    )
    assert prompt.system_message.content == "Hello Ada"
    assert PromptBuilder.use(UserMessage("x")).build().message_count == 1
    assert PromptBuilder.create().add_template(SystemTemplate("fixed")).build().message_count == 1
    assert PromptBuilder.system("s").add_user("u").build().message_count == 2
    assert PromptBuilder.user_only("u").last_user_message.content == "u"
    with pytest.raises(PromptValidationException):
        PromptBuilder.use(template).build()
    with pytest.raises(TypeError):
        PromptBuilder.use(None)
    with pytest.raises(TypeError):
        PromptBuilder.create().add_message(None)
    with pytest.raises(TypeError):
        PromptBuilder.create().add_template(None)
    with pytest.raises(ValueError):
        PromptBuilder.create().useWith("", 1)
    with pytest.raises(TypeError):
        PromptBuilder.create().useWith("x", None)
    with pytest.raises(TypeError):
        PromptBuilder.create().with_response_format(None)
    for method in ("add_system", "add_developer", "add_user", "add_assistant"):
        with pytest.raises(TypeError):
            getattr(PromptBuilder.create(), method)(None)


def test_conversation_prompt_and_windows():
    existing = AssistantMessage("answer")
    conversation = (
        Conversation.create("Chat")
        .with_system("rules")
        .add_user([TextPart("one")])
        .add_assistant("two")
        .add_assistant(existing)
        .add_message(UserMessage("three"))
    )
    assert conversation.message_count == 4
    assert conversation.messages is not conversation.messages
    assert conversation.system_message.content == "rules"
    assert conversation.to_prompt().message_count == 5
    assert conversation.to_prompt_with_window(2).message_count == 3
    assert conversation.to_prompt_with_window(99).message_count == 5
    # Clamp negatives/zero: system only (not Python's list[-0:] full-slice pitfall).
    assert conversation.to_prompt_with_window(0).message_count == 1
    assert conversation.to_prompt_with_window(-1).message_count == 1
    assert conversation.to_prompt_with_window(0).messages[0].role is MessageRole.System
    with pytest.raises(TypeError):
        conversation.add_user(None)
    with pytest.raises(TypeError):
        conversation.add_message(None)


def test_prompt_properties_metadata_variables_results_and_exceptions():
    metadata = (
        MessageMetadata.empty()
        .set_name("Name")
        .set_description("Description")
        .set_version(PromptVersion.initial())
        .set_tags(["a"])
        .add_tag("b")
        .set_author("Author")
        .set_category("Category")
        .set_language("en")
        .set_provider("Provider")
        .set_model("Model")
        .set_min_compatible_version(PromptVersion(1, 0, 0))
    )
    prompt = Prompt([SystemMessage("s"), UserMessage("u1"), UserMessage("u2")], metadata)
    assert prompt.message_count == 3
    assert prompt.system_message.content == "s"
    assert prompt.last_user_message.content == "u2"
    assert len(prompt.get_messages(MessageRole.User)) == 2
    assert "Prompt [3 messages] Name" == str(prompt)
    assert metadata.semantic_version == PromptVersion.initial()
    assert Prompt([AssistantMessage("a")]).last_user_message is None
    assert Prompt([UserMessage("u")]).system_message is None
    with pytest.raises(TypeError):
        Prompt(None)
    with pytest.raises(PromptValidationException):
        Prompt([])
    with pytest.raises(TypeError):
        metadata.set_version(None)
    with pytest.raises(TypeError):
        metadata.set_min_compatible_version(None)

    assert PromptVariable.required("x").is_required
    optional = PromptVariable.optional("x", 10, "desc")
    assert not optional.is_required and optional.default_value == 10
    with pytest.raises(ValueError):
        PromptVariable("")
    assert TemplateValidationResult.success().is_valid
    assert TemplateValidationResult.failure(["x"]).missing_variables == ["x"]
    assert TemplateValidationResult.from_errors(["bad"]).errors == ["bad"]

    default_exc = PromptValidationException()
    list_exc = PromptValidationException(["one", "two"])
    named_exc = PromptValidationException(
        missing_variables=["x", "y"], template_name="Template"
    )
    assert str(default_exc) == "Prompt validation failed."
    assert str(list_exc) == "one; two"
    assert named_exc.missing_variables == ["x", "y"]


def test_output_formats_and_constraints_render():
    formats = [
        OutputFormat.json(),
        OutputFormat.yaml(),
        OutputFormat.markdown(),
        OutputFormat.plain_text(),
        OutputFormat.bullet_points(),
        OutputFormat.steps(),
        OutputFormat.json_with_schema("{}"),
        OutputFormat.yaml_with_schema("{}"),
        OutputFormat.custom("csv", "Use CSV", "schema"),
    ]
    assert [f.type for f in formats[:6]] == [
        OutputFormat.JSON,
        OutputFormat.YAML,
        OutputFormat.MARKDOWN,
        OutputFormat.PLAIN_TEXT,
        OutputFormat.BULLETS,
        OutputFormat.STEPS,
    ]
    constraints = (
        PromptConstraints.create()
        .max_words(100)
        .min_words(10)
        .with_format(formats[0])
        .no_emojis()
        .no_tables()
        .no_code()
        .no_links()
        .must_include("Include sources")
        .must_avoid("jargon")
        .must("Be accurate")
        .not_("Speculate")
    )
    assert constraints.must_do == ["Include sources", "Be accurate"]
    assert len(constraints.must_not) == 6
    rendered = constraints.render()
    assert "100 words maximum" in rendered
    assert "Requirements:" in rendered and "Restrictions:" in rendered
    assert PromptConstraints.create().render() == ""


def test_annotations_and_catalog_counts():
    url = MessageAnnotation.url_citation("https://example.test", "Title", "quote", 1, 2)
    file = MessageAnnotation.file_citation("file", "File", "quote")
    ref = MessageAnnotation.internal_ref("section", "Section")
    assert (url.kind, url.start_index, url.end_index) == ("url_citation", 1, 2)
    assert file.file_id == "file" and ref.file_id == "section"
    with pytest.raises(ValueError):
        MessageAnnotation("")

    system_templates = [
        value
        for name, value in inspect.getmembers(SystemTemplates)
        if not name.startswith("_") and isinstance(value, SystemTemplate)
    ]
    user_templates = [
        value
        for name, value in inspect.getmembers(UserTemplates)
        if not name.startswith("_") and isinstance(value, UserTemplate)
    ]
    assert len(system_templates) == 36
    assert len(user_templates) == 29
    assert SystemTemplates.Configurable.variables == ["profession", "tone", "maxWords"]


def test_validation_reports_warnings_and_empty_message_detection():
    assert str(PromptValidationReport.success()) == "Valid"
    valid_warning = PromptValidationReport(True, warnings=["note"])
    invalid = PromptValidationReport(False, ["bad"], ["note"])
    assert valid_warning.has_warnings and str(valid_warning) == "Valid (1 warning(s))"
    assert str(invalid) == "Invalid (1 error(s), 1 warning(s))"
    validator = PromptValidator()
    with pytest.raises(TypeError):
        validator.validate(None)

    prompt = Prompt(
        [UserMessage("u"), SystemMessage("s"), SystemMessage("s2")]
        + [UserMessage("x") for _ in range(99)]
    )
    report = validator.validate(prompt)
    assert report.is_valid
    assert len(report.warnings) == 3
    no_user = validator.validate(Prompt([AssistantMessage.create_refusal("no")]))
    assert no_user.is_valid and no_user.has_warnings

    malformed = UserMessage.__new__(UserMessage)
    malformed.role = MessageRole.User
    malformed.parts = []
    malformed.content = ""
    malformed.id = "bad"
    report = validator.validate(Prompt([malformed]))
    assert not report.is_valid


def test_prompt_version_parse_compare_and_helpers():
    version = PromptVersion.parse("1.2.3-beta+build.4")
    assert str(version) == "1.2.3-beta+build.4"
    assert repr(version) == "PromptVersion(1.2.3-beta+build.4)"
    assert version.is_pre_release and not version.is_stable
    assert PromptVersion.parse("2").minor == 0
    with pytest.raises(ValueError, match="Invalid minor version"):
        PromptVersion.parse("2.bad")
    assert PromptVersion.try_parse("bad") is None
    assert PromptVersion.try_parse(None) is None
    assert version.next_major() == PromptVersion(2, 0, 0)
    assert version.next_minor() == PromptVersion(1, 3, 0)
    assert version.next_patch() == PromptVersion(1, 2, 4)
    assert version.with_pre_release("rc").pre_release == "rc"
    assert version.with_build_metadata("new").build_metadata == "new"
    assert version.to_stable().is_stable
    assert PromptVersion(1, 2, 3).is_compatible_with(PromptVersion(1, 1, 9))
    assert not PromptVersion(1, 2, 3).is_compatible_with(PromptVersion(2, 0, 0))
    assert not version.is_compatible_with(None)
    assert PromptVersion(1, 0, 0, "a") < PromptVersion(1, 0, 0, "b")
    assert PromptVersion(1, 0, 0, "b") < PromptVersion(1, 0, 0)
    assert PromptVersion(2, 0, 0) > PromptVersion(1, 9, 9)
    assert PromptVersion(1, 2, 0) >= PromptVersion(1, 1, 9)
    assert PromptVersion(1, 0, 0) <= PromptVersion(1, 0, 0)
    assert PromptVersion(1, 0, 0)._cmp(None) == 1
    assert PromptVersion(1, 0, 0) != object()
    with pytest.raises(ValueError):
        PromptVersion(-1, 0, 0)
    with pytest.raises(ValueError):
        PromptVersion(0, -1, 0)
    with pytest.raises(ValueError):
        PromptVersion(0, 0, -1)
    with pytest.raises(ValueError):
        PromptVersion.parse("")
    with pytest.raises(ValueError):
        PromptVersion.parse("1.2.3.4")


def test_version_history_and_assets():
    v1 = PromptVersion(1, 0, 0)
    beta = PromptVersion(1, 1, 0, "beta")
    v2 = PromptVersion(1, 1, 0)
    history = (
        PromptVersionHistory.create("asset")
        .add(v2, "stable", "released", "Ada")
        .add(v1, "initial")
        .add(beta, "preview", "preview")
    )
    assert history.count == 3
    assert history.latest.content == "stable"
    assert history.latest_stable.content == "stable"
    assert history.get(v1).content == "initial"
    assert history.get_content(v1) == "initial"
    assert history.get_content(PromptVersion(9, 0, 0)) is None
    assert history.contains(beta)
    assert len(history.get_range(v1, v2)) == 3
    assert history.get_change_log(v1, v2) == [
        "v1.1.0-beta: preview",
        "v1.1.0: released",
    ]
    assert str(history.get(v2)).endswith(": released")
    assert "v1.0.0" in str(history.get(v1))
    with pytest.raises(RuntimeError):
        history.add(v1, "duplicate")
    with pytest.raises(TypeError):
        history.add(None, "x")
    with pytest.raises(TypeError):
        history.add(PromptVersion(3, 0, 0), None)
    with pytest.raises(ValueError):
        PromptVersionHistory("")
    empty = PromptVersionHistory("empty")
    assert empty.latest is None and empty.latest_stable is None

    asset = (
        VersionedPromptAsset.create("prompt", v1, "content")
        .with_description("description")
        .with_author("Ada")
        .with_tags("a", "b")
        .with_change_log("created")
        .deprecate("old")
    )
    assert str(asset).endswith("[DEPRECATED]")
    assert asset.bump_major("major").change_log == "Breaking change"
    assert asset.bump_minor("minor", "feature").change_log == "feature"
    assert asset.bump_patch("patch").change_log == "Bug fix"
    with pytest.raises(ValueError):
        VersionedPromptAsset("", v1, "x")
    with pytest.raises(TypeError):
        VersionedPromptAsset("x", None, "x")
    with pytest.raises(TypeError):
        VersionedPromptAsset("x", v1, None)


def test_localized_template_exact_default_first_and_roles():
    metadata = MessageMetadata.with_name("localized")
    localized = (
        LocalizedTemplate.create(MessageRole.System)
        .add_locale("en", "Hello {{name}}")
        .add_locale("FR", "Bonjour {{name}}")
        .add_locale("fr", "Salut {{name}}")
        .with_default("fr")
        .with_metadata(metadata)
    )
    assert localized.available_locales == ["en", "fr"]
    assert localized.default_locale == "fr"
    assert localized.has_locale("FR")
    assert localized.get_content("de") == "Salut {{name}}"
    assert localized.render("en", {"name": "Ada"}).content == "Hello Ada"
    for role, expected in (
        (MessageRole.User, UserMessage),
        (MessageRole.Assistant, AssistantMessage),
        (MessageRole.Developer, DeveloperMessage),
    ):
        rendered = LocalizedTemplate(role).add_locale("en", "Hi").render("en", {})
        assert isinstance(rendered, expected)
    first = LocalizedTemplate(MessageRole.User).add_locale("es", "Hola")
    assert first.get_content("unknown") == "Hola"
    with pytest.raises(RuntimeError):
        LocalizedTemplate(MessageRole.User).get_content("en")
    with pytest.raises(RuntimeError):
        LocalizedTemplate(MessageRole.Tool).add_locale("en", "x").render("en", {})
    with pytest.raises(TypeError):
        LocalizedTemplate(None)
    with pytest.raises(ValueError):
        LocalizedTemplate(MessageRole.User).add_locale("", "x")
    with pytest.raises(ValueError):
        LocalizedTemplate(MessageRole.User).add_locale("en", "")


def test_serialization_round_trips_every_message_shape():
    serializer = PromptSerializer()
    metadata = MessageMetadata(
        name="Prompt",
        description="desc",
        category="cat",
        version="1.0.0",
        author="Ada",
        tags=["one"],
        language="en",
        provider="provider",
        model="model",
        created=datetime(2025, 1, 1),
        modified=datetime(2025, 1, 2),
        min_compatible_version="1.0.0",
    )
    annotation = MessageAnnotation.url_citation("https://example.test", "source")
    messages = [
        SystemMessage.create([TextPart("sys")], metadata, "s", "system", [annotation]),
        DeveloperMessage.create([TextPart("dev")], metadata, "d"),
        UserMessage.create(
            [
                TextPart("see"),
                ImagePart.from_url("https://example.test/i", "high"),
                ImagePart.from_base64("YWJj", "image/png"),
            ],
            metadata,
            "user",
            "u",
            [annotation],
        ),
        AssistantMessage.create_detailed(
            tool_calls=[ToolCall("call", "lookup", "{}")],
            refusal="declined",
            metadata=metadata,
            id="a",
            name="assistant",
            annotations=[annotation],
        ),
        ToolMessage("call", "result", metadata, "t"),
        FunctionMessage("legacy", "value", metadata, "f"),
    ]
    prompt = Prompt(messages, metadata, "prompt-id", OutputFormat.yaml_with_schema("type: object"))
    raw = serializer.serialize(prompt)
    restored = serializer.deserialize_prompt(raw)
    assert restored.id == "prompt-id"
    assert restored.metadata.tags == ["one"]
    assert restored.response_format.type == OutputFormat.YAML
    assert [m.role for m in restored.messages] == [m.role for m in messages]
    assert restored.messages[2].parts[1].url == "https://example.test/i"
    assert restored.messages[2].parts[2].base64_data == "YWJj"
    assert restored.messages[3].tool_calls[0].name == "lookup"
    assert restored.messages[3].refusal == "declined"
    assert restored.messages[4].tool_call_id == "call"
    assert restored.messages[5].function_name == "legacy"

    message_raw = serializer.serialize_message(messages[2])
    assert serializer.deserialize_message(message_raw).annotations[0].kind == "url_citation"
    template_raw = serializer.serialize_template(SystemTemplate.create("Hi {{name}}"))
    assert json.loads(template_raw)["variables"] == ["name"]


def test_serialization_validation_and_custom_formats():
    serializer = PromptSerializer()
    custom = PromptBuilder.user_only("x")
    custom.response_format = OutputFormat.custom("csv", "CSV only")
    assert serializer.deserialize_prompt(serializer.serialize(custom)).response_format.type == "csv"
    plain = serializer.deserialize_prompt(serializer.serialize(PromptBuilder.user_only("x")))
    assert plain.response_format is None
    with pytest.raises(TypeError):
        serializer.serialize(None)
    with pytest.raises(ValueError):
        serializer.deserialize_prompt("")
    with pytest.raises(TypeError):
        serializer.serialize_message(None)
    with pytest.raises(ValueError):
        serializer.deserialize_message("")
    with pytest.raises(TypeError):
        serializer.serialize_template(None)
    with pytest.raises(ValueError):
        serializer.deserialize_message('{"role":"user","id":"x"}')
    with pytest.raises(ValueError):
        serializer.deserialize_message('{"role":"system","id":"x","parts":[]}')

