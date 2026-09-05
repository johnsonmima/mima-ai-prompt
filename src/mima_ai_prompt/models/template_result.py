"""Result of checking template variables before render."""

from __future__ import annotations

from typing import Iterable


class TemplateValidationResult:
    """``is_valid`` plus missing names, unexpected extras, and error strings."""

    def __init__(
        self,
        is_valid: bool,
        missing_variables: Iterable[str] | None = None,
        extra_variables: Iterable[str] | None = None,
        errors: Iterable[str] | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.missing_variables = list(missing_variables or [])
        self.extra_variables = list(extra_variables or [])
        self.errors = list(errors or [])

    @classmethod
    def success(cls) -> TemplateValidationResult:
        """All required names present, no extras."""
        return cls(True)

    @classmethod
    def failure(cls, missing_variables: Iterable[str]) -> TemplateValidationResult:
        """Invalid because required names are missing."""
        missing = list(missing_variables)
        return cls(
            False,
            missing,
            errors=[f"Missing required variable: '{v}'" for v in missing],
        )

    @classmethod
    def from_errors(cls, errors: Iterable[str]) -> TemplateValidationResult:
        """Invalid with a free-form error list."""
        return cls(False, errors=errors)
