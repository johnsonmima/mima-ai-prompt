"""Role-agnostic message templates with variable discovery and rendering."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping

from mima_ai_prompt.exceptions import PromptValidationException
from mima_ai_prompt.messages import Message
from mima_ai_prompt.models import MessageMetadata, PromptVariable, TemplateValidationResult
from mima_ai_prompt.roles import MessageRole

VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")


class MessageTemplate(ABC):
    """Discovers placeholders, validates values, and renders one typed message."""

    def __init__(
        self,
        role: MessageRole,
        template_content: str,
        metadata: MessageMetadata | None = None,
        variable_defs: Iterable[PromptVariable] | None = None,
    ) -> None:
        if role is None:
            raise TypeError("role cannot be None")
        if template_content is None or not str(template_content).strip():
            raise PromptValidationException("Template content cannot be null or empty.")
        self.role = role
        self.template_content = template_content
        self.metadata = metadata or MessageMetadata.empty()
        self.variable_defs = list(variable_defs or [])

    @property
    def variables(self) -> list[str]:
        """``{{name}}`` identifiers in first-seen order, then unused ``variable_defs``.

        Names are ``[A-Za-z0-9_]+``. Whitespace inside braces is not matched.
        """
        seen: list[str] = []
        for match in VARIABLE_PATTERN.finditer(self.template_content):
            name = match.group(1)
            if name not in seen:
                seen.append(name)
        for spec in self.variable_defs:
            if spec.name not in seen:
                seen.append(spec.name)
        return seen

    def _defs_by_name(self) -> dict[str, PromptVariable]:
        return {spec.name: spec for spec in self.variable_defs}

    def _apply_defaults(self, variables: Mapping[str, Any]) -> dict[str, Any]:
        values = dict(variables)
        for spec in self.variable_defs:
            if (spec.name not in values or values[spec.name] is None) and (
                not spec.is_required and spec.default_value is not None
            ):
                values[spec.name] = spec.default_value
        return values

    def validate(self, variables: Mapping[str, Any]) -> TemplateValidationResult:
        """Fail on missing required names or extra keys."""
        values = self._apply_defaults(variables)
        allowed = set(self.variables)
        defs = self._defs_by_name()
        missing: list[str] = []
        for name in self.variables:
            spec = defs.get(name)
            required = spec.is_required if spec is not None else True
            if required and (name not in values or values[name] is None):
                missing.append(name)
        extra = [k for k in variables if k not in allowed]
        errors = [f"Missing required variable: '{v}'" for v in missing]
        errors.extend(f"Unexpected variable: '{v}'" for v in extra)
        if not missing and not extra:
            return TemplateValidationResult.success()
        return TemplateValidationResult(False, missing, extra, errors)

    def render(self, variables: Mapping[str, Any] | object) -> Message:
        """Substitute placeholders and return a typed message."""
        if not isinstance(variables, Mapping):
            variables = object_to_dict(variables)
        values = self._apply_defaults(variables)
        validation = self.validate(variables)
        if not validation.is_valid:
            raise PromptValidationException(validation.errors)
        rendered = VARIABLE_PATTERN.sub(
            lambda m: (
                str(values[m.group(1)])
                if m.group(1) in values and values[m.group(1)] is not None
                else m.group(0)
            ),
            self.template_content,
        )
        return self._create_message(rendered)

    @abstractmethod
    def _create_message(self, rendered_content: str) -> Message: ...


def object_to_dict(obj: object) -> dict[str, Any]:
    if isinstance(obj, Mapping):
        return dict(obj)
    result: dict[str, Any] = {}
    for key, value in vars(obj).items():
        if value is not None and not key.startswith("_"):
            result[key] = value
    return result
