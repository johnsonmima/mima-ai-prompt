"""Port of ExceptionTests.cs."""

from mima_ai_prompt import PromptValidationException


def test_ctor_single_message_sets_errors_and_message():
    ex = PromptValidationException("Something went wrong.")
    assert str(ex) == "Something went wrong."
    assert ex.errors == ["Something went wrong."]
    assert ex.missing_variables == []


def test_ctor_multiple_errors_joins_message_and_sets_errors():
    errors = ["Error 1", "Error 2"]
    ex = PromptValidationException(errors)
    assert str(ex) == "Error 1; Error 2"
    assert ex.errors == errors
    assert ex.missing_variables == []


def test_ctor_missing_variables_with_template_name_sets_message_and_collections():
    missing = ["name", "topic"]
    ex = PromptValidationException(
        missing_variables=missing, template_name="MyTemplate"
    )
    assert "MyTemplate" in str(ex)
    assert "name" in str(ex)
    assert "topic" in str(ex)
    assert ex.missing_variables == missing
    assert len(ex.errors) == 2
    assert "name" in ex.errors[0]


def test_exception_is_exception_subtype():
    ex = PromptValidationException("error")
    assert isinstance(ex, Exception)
