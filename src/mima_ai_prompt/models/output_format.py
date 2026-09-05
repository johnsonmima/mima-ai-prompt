"""Instructions describing how a model response should be shaped."""

from __future__ import annotations


class OutputFormat:
    """A format name, instruction text, and optional schema string.

    Stored on ``Prompt.response_format``. The host maps this to a vendor API.
    ``type`` is one of the class constants (``JSON``, ``YAML``, …) unless
    ``custom`` is used.
    """

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plaintext"
    BULLETS = "bullets"
    STEPS = "steps"

    def __init__(
        self, type: str, instructions: str, schema: str | None = None
    ) -> None:
        self.type = type
        self.instructions = instructions
        self.schema = schema

    @classmethod
    def json(cls, schema: str | None = None) -> OutputFormat:
        """Ask for JSON only (no markdown fences)."""
        return cls(
            cls.JSON,
            "Respond with valid JSON only. Do not include markdown code fences or any other text.",
            schema,
        )

    @classmethod
    def yaml(cls, schema: str | None = None) -> OutputFormat:
        """Ask for YAML only (no markdown fences)."""
        return cls(
            cls.YAML,
            "Respond with valid YAML only. Do not include markdown code fences or any other text.",
            schema,
        )

    @classmethod
    def markdown(cls) -> OutputFormat:
        """Ask for well-formed Markdown."""
        return cls(
            cls.MARKDOWN,
            "Respond using well-formatted Markdown with proper headers, code blocks, and lists.",
        )

    @classmethod
    def plain_text(cls) -> OutputFormat:
        """Ask for unformatted plain text."""
        return cls(
            cls.PLAIN_TEXT,
            "Respond with plain text only. No formatting, no markdown, no code blocks.",
        )

    @classmethod
    def bullet_points(cls) -> OutputFormat:
        """Ask for a concise bullet list."""
        return cls(
            cls.BULLETS,
            "Respond using bullet points. Each point should be concise and actionable.",
        )

    @classmethod
    def steps(cls) -> OutputFormat:
        """Ask for numbered, self-contained steps."""
        return cls(
            cls.STEPS,
            "Respond with numbered steps. Each step should be clear and self-contained.",
        )

    @classmethod
    def json_with_schema(cls, schema: str) -> OutputFormat:
        """Ask for JSON that matches ``schema``."""
        return cls(
            cls.JSON,
            f"Respond with valid JSON only matching this schema:\n{schema}",
            schema,
        )

    @classmethod
    def yaml_with_schema(cls, schema: str) -> OutputFormat:
        """Ask for YAML that matches ``schema``."""
        return cls(
            cls.YAML,
            f"Respond with valid YAML only matching this schema:\n{schema}",
            schema,
        )

    @classmethod
    def custom(
        cls, type: str, instructions: str, schema: str | None = None
    ) -> OutputFormat:
        """Build an arbitrary format with your own instructions."""
        return cls(type, instructions, schema)
