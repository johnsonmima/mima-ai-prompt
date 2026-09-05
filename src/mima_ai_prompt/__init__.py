"""Mima AI Prompt — typed prompt composition for Python.

Composes prompts as structured objects and canonical JSON. Does not call models,
map vendor APIs, run tools, or include an agent runtime.
"""

from mima_ai_prompt.builder import PromptBuilder
from mima_ai_prompt.catalog import SystemTemplates, UserTemplates
from mima_ai_prompt.content import ContentPart, ImagePart, TextPart
from mima_ai_prompt.conversation import Conversation
from mima_ai_prompt.exceptions import PromptValidationException
from mima_ai_prompt.localization import LocalizedTemplate
from mima_ai_prompt.messages import (
    AssistantMessage,
    DeveloperMessage,
    FunctionMessage,
    Message,
    SystemMessage,
    ToolMessage,
    UserMessage,
)
from mima_ai_prompt.models import (
    MessageAnnotation,
    MessageMetadata,
    OutputFormat,
    Prompt,
    PromptConstraints,
    PromptVariable,
    PromptVersion,
    TemplateValidationResult,
    ToolCall,
)
from mima_ai_prompt.roles import MessageRole
from mima_ai_prompt.serialization import PromptSerializer
from mima_ai_prompt.templates import (
    AssistantTemplate,
    DeveloperTemplate,
    MessageTemplate,
    SystemTemplate,
    UserTemplate,
)
from mima_ai_prompt.validation import PromptValidationReport, PromptValidator
from mima_ai_prompt.versioning import (
    PromptVersionHistory,
    VersionedPromptAsset,
    VersionEntry,
)

__version__ = "1.0.0"

__all__ = [
    "AssistantMessage",
    "AssistantTemplate",
    "ContentPart",
    "Conversation",
    "DeveloperMessage",
    "DeveloperTemplate",
    "FunctionMessage",
    "ImagePart",
    "LocalizedTemplate",
    "Message",
    "MessageAnnotation",
    "MessageMetadata",
    "MessageRole",
    "MessageTemplate",
    "OutputFormat",
    "Prompt",
    "PromptBuilder",
    "PromptConstraints",
    "PromptSerializer",
    "PromptValidationException",
    "PromptValidationReport",
    "PromptValidator",
    "PromptVariable",
    "PromptVersion",
    "PromptVersionHistory",
    "SystemMessage",
    "SystemTemplate",
    "SystemTemplates",
    "TemplateValidationResult",
    "TextPart",
    "ToolCall",
    "ToolMessage",
    "UserMessage",
    "UserTemplate",
    "UserTemplates",
    "VersionEntry",
    "VersionedPromptAsset",
]
