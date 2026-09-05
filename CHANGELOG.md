# Changelog

All notable changes to mima-ai-prompt will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Template variables on `PromptBuilder` use `.useWith(name, value)` instead of `.with_`.

### Fixed

- Documented Python import as `mima_ai_prompt` (PyPI name remains `mima-ai-prompt`).
- Shipped `py.typed` so type checkers treat the wheel as typed.
- Release workflow refuses a git tag that does not match `pyproject.toml` version.

## [1.0.0] - 2026-08-25

Initial Python release (API parity with Mima.AI.Prompt for .NET). This package **composes** prompts: typed messages, templates, validation, in-memory versioning, and canonical JSON. It does **not** call models, map vendor chat APIs, run tools, or ship an agent runtime.

### Added

- Messages and roles: `system`, `developer`, `user`, `assistant`, `tool`, `function`. Bodies are **parts** (`TextPart`, `ImagePart`). `content` is concatenated text in memory; `PromptSerializer` writes `parts` only.
- Templates with `{{variable}}` discovery; system/user/assistant/developer templates; catalog (`SystemTemplates` / `UserTemplates`).
- `PromptBuilder`, `Conversation`, `PromptValidator`, `PromptConstraints`, `OutputFormat`.
- `PromptSerializer` canonical JSON; host maps to OpenAI, Anthropic, Grok, etc.
- `PromptVersion`, `VersionedPromptAsset`, `PromptVersionHistory` (in-memory).
- `LocalizedTemplate` (per-locale strings; you pass the locale).
