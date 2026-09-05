"""Port of MessageRoleTests.cs."""

import pytest

from mima_ai_prompt import MessageRole


@pytest.mark.parametrize("input_value", ["system", "SYSTEM", "System", " system "])
def test_parse_system_returns_system_role(input_value):
    assert MessageRole.parse(input_value) is MessageRole.System


@pytest.mark.parametrize("input_value", ["developer", "DEVELOPER", "Developer"])
def test_parse_developer_returns_developer_role(input_value):
    assert MessageRole.parse(input_value) is MessageRole.Developer


@pytest.mark.parametrize("input_value", ["user", "USER", "User"])
def test_parse_user_returns_user_role(input_value):
    assert MessageRole.parse(input_value) is MessageRole.User


@pytest.mark.parametrize("input_value", ["assistant", "ASSISTANT", "Assistant"])
def test_parse_assistant_returns_assistant_role(input_value):
    assert MessageRole.parse(input_value) is MessageRole.Assistant


@pytest.mark.parametrize("input_value", ["tool", "TOOL", "Tool"])
def test_parse_tool_returns_tool_role(input_value):
    assert MessageRole.parse(input_value) is MessageRole.Tool


@pytest.mark.parametrize("input_value", ["function", "FUNCTION", "Function"])
def test_parse_function_returns_function_role(input_value):
    assert MessageRole.parse(input_value) is MessageRole.Function


def test_parse_unknown_role_throws():
    with pytest.raises(ValueError, match="Unknown message role"):
        MessageRole.parse("wizard")


@pytest.mark.parametrize("input_value", [None, "", "   "])
def test_parse_null_or_empty_throws(input_value):
    with pytest.raises(ValueError, match="Role name cannot be null or empty"):
        MessageRole.parse(input_value)


def test_try_parse_valid_role_returns_role():
    assert MessageRole.try_parse("user") is MessageRole.User


def test_try_parse_invalid_role_returns_none():
    assert MessageRole.try_parse("notarole") is None


def test_try_parse_null_returns_none():
    assert MessageRole.try_parse(None) is None


def test_try_parse_empty_returns_none():
    assert MessageRole.try_parse("") is None


def test_all_returns_six_roles():
    roles = MessageRole.all()
    assert len(roles) == 6
    for expected in (
        MessageRole.System,
        MessageRole.Developer,
        MessageRole.User,
        MessageRole.Assistant,
        MessageRole.Tool,
        MessageRole.Function,
    ):
        assert expected in roles


def test_equality_same_role_returns_true():
    system = MessageRole.System
    assert system == MessageRole.System
    assert MessageRole.System != MessageRole.User


def test_equals_object_works_correctly():
    assert MessageRole.System == MessageRole.System
    assert MessageRole.System != MessageRole.User
    assert MessageRole.System != "system"
    assert MessageRole.System != None


def test_get_hash_code_matches_name_hash_code():
    assert hash(MessageRole.System) == hash("system")


def test_to_string_returns_name():
    assert str(MessageRole.System) == "system"
    assert str(MessageRole.User) == "user"


@pytest.mark.parametrize(
    "role,expected",
    [
        (MessageRole.System, 0),
        (MessageRole.Developer, 1),
        (MessageRole.User, 2),
        (MessageRole.Assistant, 3),
        (MessageRole.Tool, 4),
        (MessageRole.Function, 5),
    ],
)
def test_priority_has_expected_value(role, expected):
    assert role.priority == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        (MessageRole.System, "system"),
        (MessageRole.Developer, "developer"),
        (MessageRole.User, "user"),
        (MessageRole.Assistant, "assistant"),
        (MessageRole.Tool, "tool"),
        (MessageRole.Function, "function"),
    ],
)
def test_name_has_expected_value(role, expected):
    assert role.name == expected


def test_description_is_not_empty_for_all_roles():
    for role in MessageRole.all():
        assert role.description and role.description.strip()


def test_description_for_each_role_is_specific():
    assert "identity" in MessageRole.System.description
    assert "system" in MessageRole.Developer.description
    assert "Human" in MessageRole.User.description
    assert "AI responses" in MessageRole.Assistant.description
    assert "tool" in MessageRole.Tool.description
    assert "function" in MessageRole.Function.description
