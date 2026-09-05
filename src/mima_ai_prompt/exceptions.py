"""Errors raised when a prompt or template fails validation."""

from __future__ import annotations


class PromptValidationException(Exception):
    """Validation failure with ``errors`` and optional ``missing_variables``."""

    def __init__(
        self,
        message: str | list[str] | None = None,
        *,
        missing_variables: list[str] | None = None,
        template_name: str | None = None,
    ) -> None:
        if missing_variables is not None and template_name is not None:
            names = ", ".join(missing_variables)
            msg = f"Template '{template_name}' is missing required variables: {names}"
            errors = [f"Missing required variable: '{v}'" for v in missing_variables]
            super().__init__(msg)
            self.errors = errors
            self.missing_variables = list(missing_variables)
            return

        if isinstance(message, list):
            errors = list(message)
            super().__init__("; ".join(errors))
            self.errors = errors
            self.missing_variables = []
            return

        msg = message or "Prompt validation failed."
        super().__init__(msg)
        self.errors = [msg]
        self.missing_variables: list[str] = []
