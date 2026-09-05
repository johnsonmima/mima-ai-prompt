"""Named template variables, required or optional with a default."""

from __future__ import annotations

from typing import Iterable


class PromptVariable:
    """Metadata for one ``{{name}}`` placeholder: required flag, default, examples."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        default_value: object | None = None,
        is_required: bool = True,
        type_hint: str | None = None,
        examples: Iterable[str] | None = None,
    ) -> None:
        if not name or not str(name).strip():
            raise ValueError("Variable name cannot be null or empty.")
        self.name = name
        self.description = description
        self.default_value = default_value
        self.is_required = is_required
        self.type_hint = type_hint
        self.examples = list(examples) if examples is not None else []

    @classmethod
    def required(cls, name: str, description: str | None = None) -> PromptVariable:
        """A placeholder that must be supplied at render time."""
        return cls(name, description, is_required=True)

    @classmethod
    def optional(
        cls, name: str, default_value: object, description: str | None = None
    ) -> PromptVariable:
        """A placeholder filled from ``default_value`` when omitted."""
        return cls(name, description, default_value, is_required=False)
