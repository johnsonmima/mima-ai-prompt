# Contributing to mima-ai-prompt

Thanks for helping improve this library. This document explains how to contribute effectively to an open-source Python package.

## Why this file exists

Open-source projects receive contributions from people who have never met the maintainers. Clear contribution rules reduce friction, keep PR review focused, and protect release quality (tests, API stability, license compatibility).

## Code of Conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Ways to contribute

- Report bugs and request features via [GitHub Issues](https://github.com/johnsonmima/mima-ai-prompt/issues)
- Improve documentation (README, docstrings, samples)
- Add or fix unit tests (prefer README-aligned cases)
- Propose API improvements via an Issue **before** a large PR

## Development setup

1. Install [uv](https://docs.astral.sh/uv/) and Python 3.10+.
2. Clone the repository:

```bash
git clone https://github.com/johnsonmima/mima-ai-prompt.git
cd mima-ai-prompt
```

3. Sync and install:

```bash
uv sync --all-groups
```

4. Run tests with coverage (≥ 95% line):

```bash
uv run pytest --cov=mima_ai_prompt --cov-report=term-missing --cov-fail-under=95
```

5. Build the package:

```bash
uv build
```

## Branching & pull requests

The full procedure is in [PR.md](PR.md). Short form:

1. Fork the repository (or create a branch if you have write access).
2. Update local `main` from the remote, then create a feature branch:

```bash
git checkout -b feature/short-description
```

3. Keep changes focused. Prefer small PRs over multi-concern mega-PRs.
4. Ensure all tests pass and new public APIs have tests.
5. Update `CHANGELOG.md` under `[Unreleased]` when behavior or API surface changes.
6. Open a Pull Request against `main`. Fill in the PR template.

### PR requirements

- [ ] Tests green on CI (Python 3.10–3.13)
- [ ] Unit tests added/updated; coverage ≥ 95%
- [ ] Docstrings on new public members
- [ ] No secrets, credentials, or personal paths committed
- [ ] `CHANGELOG.md` updated when user-facing
- [ ] Follows existing naming: PyPI package `mima-ai-prompt`, import `mima_ai_prompt`
- [ ] If you change dependencies, run `uv sync` and commit `uv.lock` (CI uses `--locked`)

## Coding standards

- Prefer immutable / value-like types for domain objects (messages, prompts).
- Keep the public API on prompt composition, validation, and canonical JSON. Do not add HTTP clients or vendor request bodies.
- Use `snake_case` for methods; factories mirror the .NET API where practical (`create`, `from_url`).
- `with` is a Python keyword — template variables use `.useWith(name, value)`.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
