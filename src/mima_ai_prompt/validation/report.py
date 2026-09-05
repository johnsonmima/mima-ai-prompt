"""Outcome of structural prompt checks."""

from __future__ import annotations


class PromptValidationReport:
    """``is_valid``, blocking ``errors``, and non-blocking ``warnings``."""

    def __init__(
        self,
        is_valid: bool,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.errors = list(errors or [])
        self.warnings = list(warnings or [])

    @property
    def has_warnings(self) -> bool:
        """True when at least one warning was recorded."""
        return len(self.warnings) > 0

    @classmethod
    def success(cls) -> PromptValidationReport:
        """Valid prompt with no errors or warnings."""
        return cls(True)

    def __str__(self) -> str:
        if self.is_valid:
            if self.has_warnings:
                return f"Valid ({len(self.warnings)} warning(s))"
            return "Valid"
        return f"Invalid ({len(self.errors)} error(s), {len(self.warnings)} warning(s))"
