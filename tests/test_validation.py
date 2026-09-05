"""Port of ValidationTests.cs."""

from types import SimpleNamespace

import pytest

from mima_ai_prompt import (
    MessageRole,
    Prompt,
    PromptValidationReport,
    PromptValidator,
    SystemMessage,
    UserMessage,
)


class _FakeMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content
        self.parts = []
        self.name = None
        self.annotations = []
        self.metadata = None
        self.id = "fake"


class _FakeEmptyPrompt:
    messages = []
    metadata = None
    id = "empty"
    message_count = 0
    response_format = None


def test_validate_empty_message_list_returns_error_and_short_circuits():
    report = PromptValidator().validate(_FakeEmptyPrompt())
    assert report.is_valid is False
    assert len(report.errors) == 1
    assert "must contain at least one message" in report.errors[0]
    assert report.warnings == []


def test_validate_null_prompt_throws():
    with pytest.raises(TypeError):
        PromptValidator().validate(None)


def test_validate_unmatched_tool_message_is_error():
    from mima_ai_prompt import ToolMessage

    report = PromptValidator().validate(Prompt([ToolMessage("missing", "result")]))
    assert not report.is_valid
    assert any("does not match" in e for e in report.errors)


def test_validate_empty_content_message_adds_error():
    # Concrete messages reject empty content; use a duck-typed fake like C#.
    stand_in = SimpleNamespace(
        message_count=1,
        messages=[_FakeMessage(MessageRole.User, "   ")],
    )
    report = PromptValidator().validate(stand_in)
    assert report.is_valid is False
    assert any("empty content" in e for e in report.errors)


def test_validate_system_not_first_adds_warning():
    prompt = Prompt([UserMessage("hi"), SystemMessage("sys")])
    report = PromptValidator().validate(prompt)
    assert any(
        "System message should typically be the first" in w for w in report.warnings
    )


def test_validate_system_first_no_warning_about_order():
    prompt = Prompt([SystemMessage("sys"), UserMessage("hi")])
    report = PromptValidator().validate(prompt)
    assert not any("should typically be the first" in w for w in report.warnings)


def test_validate_multiple_system_messages_adds_warning():
    prompt = Prompt([SystemMessage("sys1"), SystemMessage("sys2"), UserMessage("hi")])
    report = PromptValidator().validate(prompt)
    assert any("2 system messages" in w for w in report.warnings)


def test_validate_no_user_message_adds_warning():
    prompt = Prompt([SystemMessage("sys")])
    report = PromptValidator().validate(prompt)
    assert any("does not contain a user message" in w for w in report.warnings)


def test_validate_has_user_message_no_user_warning():
    prompt = Prompt([UserMessage("hi")])
    report = PromptValidator().validate(prompt)
    assert not any("does not contain a user message" in w for w in report.warnings)


def test_validate_more_than_100_messages_adds_warning():
    messages = [UserMessage(f"message {i}") for i in range(101)]
    report = PromptValidator().validate(Prompt(messages))
    assert any("101 messages" in w for w in report.warnings)


def test_validate_valid_prompt_returns_success_with_no_warnings():
    prompt = Prompt([SystemMessage("sys"), UserMessage("hi")])
    report = PromptValidator().validate(prompt)
    assert report.is_valid
    assert report.errors == []
    assert report.warnings == []


def test_prompt_validation_report_success_is_valid_with_no_issues():
    report = PromptValidationReport.success()
    assert report.is_valid
    assert report.has_warnings is False
    assert report.errors == []
    assert report.warnings == []


def test_prompt_validation_report_to_string_valid_no_warnings():
    assert str(PromptValidationReport.success()) == "Valid"


def test_prompt_validation_report_to_string_valid_with_warnings():
    report = PromptValidationReport(True, warnings=["warn1", "warn2"])
    assert str(report) == "Valid (2 warning(s))"
    assert report.has_warnings


def test_prompt_validation_report_to_string_invalid():
    report = PromptValidationReport(False, errors=["err1"], warnings=["warn1"])
    assert str(report) == "Invalid (1 error(s), 1 warning(s))"


def test_prompt_validation_report_ctor_defaults_to_empty_collections():
    report = PromptValidationReport(True)
    assert report.errors == []
    assert report.warnings == []
