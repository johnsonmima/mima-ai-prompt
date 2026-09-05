# mima-ai-prompt

[![CI](https://github.com/johnsonmima/mima-ai-prompt/actions/workflows/ci.yml/badge.svg)](https://github.com/johnsonmima/mima-ai-prompt/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mima-ai-prompt.svg)](https://pypi.org/project/mima-ai-prompt/)

A typed, fluent **prompt engineering** library for Python. Build, validate, and serialize prompts as **canonical JSON**.

**This package composes prompts.** It does not call models, run tools, or emit a vendor chat request body. You own HTTP and the mapping to whatever API you use today.

Python counterpart of [.NET Mima.AI.Prompt](https://www.nuget.org/packages/Mima.AI.Prompt) — same domain model and parts-first JSON shape.

**Repository:** <https://github.com/johnsonmima/mima-ai-prompt>

## Why mima-ai-prompt?

Most prompt code treats prompts as strings. That works for a few files and then falls apart:

- Prompts are duplicated across projects
- Template variables are inconsistent
- Missing placeholders are not caught until a model call fails
- A prompt has no version, no check before you send it, and no document you can save and load again
- Sharing a prompt catalog across apps means copy-paste

**mima-ai-prompt** treats prompts as structured, reusable objects. Vendor chat schemas change often; the JSON this library serializes is **this domain**, so tests and storage stay stable while your host maps to OpenAI, Anthropic, Grok, or anything else.

```python
from mima_ai_prompt import (
    PromptBuilder,
    PromptSerializer,
    PromptValidator,
    SystemTemplate,
    SystemTemplates,
    UserTemplates,
    LocalizedTemplate,
    MessageRole,
    Conversation,
    PromptVersionHistory,
    PromptVersion,
)
```

### Define the prompt once and reuse it

```python
class AppPrompts:
    SupportAgent = SystemTemplate.create(
        "SupportAgent",
        "You are a support agent for {{product}}. Be concise. Never invent policy.",
    )

api_prompt = (
    PromptBuilder.use(AppPrompts.SupportAgent)
    .useWith("product", "Billing")
    .add_user("Why was I charged twice?")
    .build()
)

job_prompt = (
    PromptBuilder.use(AppPrompts.SupportAgent)
    .useWith("product", "Shipping")
    .add_user(ticket_body)
    .build()
)
```

`with` is a Python keyword, so template variables use `.useWith(name, value)`.

`PromptSerializer().serialize(api_prompt)` stores the body as **`parts`**. In Python, `message.content` is that same text joined into one string for logging and tests; it is not a second JSON field.

```json
{
  "messages": [
    {
      "role": "system",
      "parts": [{ "type": "text", "text": "You are a support agent for Billing. Be concise. Never invent policy." }],
      "metadata": { "name": "SupportAgent" }
    },
    {
      "role": "user",
      "parts": [{ "type": "text", "text": "Why was I charged twice?" }]
    }
  ]
}
```

#### `quick` vs a named template

```python
from mima_ai_prompt import PromptBuilder

one_off = PromptBuilder.quick("Be brief.", "Summarize this email.")
```

### Named variables, discovered from the template

```python
template = SystemTemplate.create(
    "You are a {{profession}}. Use a {{tone}} tone. Limit responses to {{maxWords}} words."
)
for name in template.variables:
    print(name)  # profession, tone, maxWords

prompt = (
    PromptBuilder.use(SystemTemplates.Configurable)
    .useWith("profession", "Teacher")
    .useWith("tone", "Friendly")
    .useWith("maxWords", "200")
    .add_user("Explain generics in Python")
    .build()
)
```

### Catch missing placeholders before you call a model

```python
template = SystemTemplate.create("You are a {{profession}}. Product: {{product}}.")
check = template.validate({"profession": "Teacher"})
# check.is_valid == False; MissingVariables: product

# Raises PromptValidationException — never reaches your HTTP client
prompt = (
    PromptBuilder.use(template)
    .useWith("profession", "Teacher")
    .add_user("Hello")
    .build()
)
```

### Validate, version, and persist the prompt as JSON

```python
from mima_ai_prompt import PromptBuilder, PromptSerializer, PromptValidator

prompt_v1 = (
    PromptBuilder.system("You are a helpful assistant.")
    .add_user("Explain DI.")
    .with_name("ExplainDI")
    .build()
)
PromptValidator().validate(prompt_v1)

serializer = PromptSerializer()
json_text = serializer.serialize(prompt_v1)
restored = serializer.deserialize_prompt(json_text)
```

This package turns a `Prompt` into a JSON string (`PromptSerializer`) and keeps a list of versions in memory (`PromptVersionHistory`). It does not write files or talk to a database — you choose where the JSON lives.

```python
from mima_ai_prompt import PromptVersion, PromptVersionHistory

history = PromptVersionHistory.create("ExplainDI")
history.add(PromptVersion.create(1, 0, 0), prompt_v1, "Initial", "platform")

production = history.get_content(PromptVersion.create(1, 0, 0))
staging = (history.latest_stable or history.latest).content
```

### Same template, more than one language

```python
support = (
    LocalizedTemplate.create(MessageRole.System)
    .add_locale("en", "You are a support agent for {{product}}. Be concise.")
    .add_locale("fr", "Vous êtes un agent de support pour {{product}}. Soyez concis.")
    .with_default("en")
)
system = support.render("fr", {"product": "Billing"})
prompt = PromptBuilder.create().add_message(system).add_user("Pourquoi ?").build()
```

## What this is (and is not)

| This library **does** | This library **does not** |
|---|---|
| Typed messages, `TextPart` / `ImagePart`, templates, `{{variables}}`, validation, versioning | HTTP / SDK calls |
| `PromptBuilder` / `Conversation` → a `Prompt` you can test and serialize | An agent loop that talks to a model |
| `PromptSerializer` persist / round-trip | Vendor request JSON (`tools[]`, chat completions, …) |
| Store `ToolCall` / `ToolMessage` on the prompt | Execute tools or register delegates |

## What it supports

- **Messages:** `system`, `developer`, `user`, `assistant`, `tool`, `function`
- **Content:** `TextPart`, `ImagePart` (URL or base64 + MIME type)
- **Composition:** `PromptBuilder`, catalog templates (`SystemTemplates` / `UserTemplates`), `Conversation`
- **Transcript:** `ToolCall`, `ToolMessage`, assistant refusal
- **Quality:** `PromptValidator`, `PromptConstraints.render()`, `OutputFormat` on `Prompt`
- **Persistence:** `PromptSerializer` round-trip JSON
- **Versioning:** `PromptVersion`, `VersionedPromptAsset`, `PromptVersionHistory`
- **Localization:** `LocalizedTemplate`

**`Parts` is the stored body.** **`content` is not a second copy** — it is the concatenation of text parts for logging and tests.

## Installation

```bash
uv add mima-ai-prompt
# or
pip install mima-ai-prompt
```

Install the PyPI name `mima-ai-prompt`. Import the module as `mima_ai_prompt` (hyphens are not valid in Python import names).

## Development

```bash
uv sync --all-groups
uv run pytest --cov=mima_ai_prompt --cov-fail-under=95
uv build
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [PR.md](PR.md), and [GITHUB.md](GITHUB.md) for CI, release, and Trusted Publishing.

## License

MIT — Copyright (c) 2026 Johnson Olusegun
