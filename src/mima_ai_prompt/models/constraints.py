"""Word limits, format, and must/must-not rules rendered as instruction text."""

from __future__ import annotations

from mima_ai_prompt.models.output_format import OutputFormat


class PromptConstraints:
    """Fluent builder for a block of response rules.

    Attach via ``PromptBuilder.with_constraints``; ``render`` produces the text.
    """

    def __init__(self) -> None:
        self.max_word_count: int | None = None
        self.min_word_count: int | None = None
        self.format: OutputFormat | None = None
        self._positive: list[str] = []
        self._negative: list[str] = []

    @property
    def must_do(self) -> list[str]:
        """Copy of positive requirements."""
        return list(self._positive)

    @property
    def must_not(self) -> list[str]:
        """Copy of restrictions."""
        return list(self._negative)

    @classmethod
    def create(cls) -> PromptConstraints:
        """Empty constraints object."""
        return cls()

    def max_words(self, count: int) -> PromptConstraints:
        """Cap the response at ``count`` words."""
        self.max_word_count = count
        return self

    def min_words(self, count: int) -> PromptConstraints:
        """Require at least ``count`` words."""
        self.min_word_count = count
        return self

    def no_emojis(self) -> PromptConstraints:
        """Forbid emoji in the response."""
        self._negative.append("Do not use emojis.")
        return self

    def no_tables(self) -> PromptConstraints:
        """Forbid tables."""
        self._negative.append("Do not use tables.")
        return self

    def no_code(self) -> PromptConstraints:
        """Forbid fenced code blocks."""
        self._negative.append("Do not include code blocks.")
        return self

    def no_links(self) -> PromptConstraints:
        """Forbid URLs and links."""
        self._negative.append("Do not include URLs or links.")
        return self

    def must_include(self, requirement: str) -> PromptConstraints:
        """Add a free-form requirement."""
        self._positive.append(requirement)
        return self

    def must_avoid(self, prohibition: str) -> PromptConstraints:
        """Add a restriction prefixed with ``Avoid:``."""
        self._negative.append(f"Avoid: {prohibition}")
        return self

    def with_format(self, format: OutputFormat) -> PromptConstraints:
        """Include ``format.instructions`` in the rendered block."""
        self.format = format
        return self

    def must(self, constraint: str) -> PromptConstraints:
        """Alias for ``must_include``."""
        self._positive.append(constraint)
        return self

    def not_(self, constraint: str) -> PromptConstraints:
        """Add a restriction with no extra prefix."""
        self._negative.append(constraint)
        return self

    def render(self) -> str:
        """Join word limits, format instructions, requirements, and restrictions."""
        parts: list[str] = []
        if self.max_word_count is not None:
            parts.append(f"Limit your response to {self.max_word_count} words maximum.")
        if self.min_word_count is not None:
            parts.append(f"Your response must be at least {self.min_word_count} words.")
        if self.format is not None:
            parts.append(self.format.instructions)
        if self._positive:
            parts.append("Requirements:")
            parts.extend(f"- {c}" for c in self._positive)
        if self._negative:
            parts.append("Restrictions:")
            parts.extend(f"- {c}" for c in self._negative)
        return "\n".join(parts)
