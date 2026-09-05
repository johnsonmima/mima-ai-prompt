"""Built-in user-message templates for common request patterns."""

from __future__ import annotations

from mima_ai_prompt._utils import catalog_text
from mima_ai_prompt.templates import UserTemplate


def _usr(name: str, body: str) -> UserTemplate:
    return UserTemplate.create(name, catalog_text(body))


class UserTemplates:
    """Named user-request templates (Summarize, ReviewCode, Rag, …) with ``{{placeholders}}``."""

    Summarize = _usr(
        "Summarize",
        "        Summarize the following content in {{style}} style:\n\n        {{content}}\n        ",
    )

    Translate = _usr(
        "Translate",
        "        Translate the following text to {{targetLanguage}}:\n\n        {{text}}\n        ",
    )

    ExtractEntities = _usr(
        "Extract Entities",
        "        Extract all {{entityType}} entities from the following text. Return them as a JSON array.\n\n        {{text}}\n        ",
    )

    ReviewResume = _usr(
        "Review Resume",
        "        Review the following resume for a {{role}} position.\n        Provide: Strengths, Weaknesses, Suggestions for improvement.\n\n        {{resume}}\n        ",
    )

    GenerateSql = _usr(
        "Generate SQL",
        "        Given the following table schema:\n        {{schema}}\n\n        Write a SQL query to: {{question}}\n        ",
    )

    GenerateDocumentation = _usr(
        "Generate Documentation",
        "        Generate {{documentationType}} documentation for the following code:\n\n        ```{{language}}\n        {{code}}\n        ```\n        ",
    )

    GenerateTests = _usr(
        "Generate Tests",
        "        Write unit tests for the following {{language}} code using {{framework}}:\n\n        ```{{language}}\n        {{code}}\n        ```\n\n        Cover: happy path, edge cases, and error scenarios.\n        ",
    )

    ExplainConcept = _usr(
        "Explain Concept",
        "        Explain {{topic}} in simple terms.\n        Use analogies and examples.\n        Target audience: {{audience}}.\n        ",
    )

    ReviewCode = _usr(
        "Review Code",
        "        Review the following {{language}} code for:\n        - Performance issues\n        - Security vulnerabilities\n        - Maintainability concerns\n        - Best practice violations\n\n        ```{{language}}\n        {{code}}\n        ```\n        ",
    )

    ConvertToJson = _usr(
        "Convert to JSON",
        "        Convert the following data into a well-structured JSON format:\n\n        {{data}}\n        ",
    )

    GenerateEmail = _usr(
        "Generate Email",
        "        Write a professional email.\n        Audience: {{audience}}\n        Tone: {{tone}}\n        Purpose: {{purpose}}\n        Key points to include: {{keyPoints}}\n        ",
    )

    Rag = _usr(
        "RAG",
        "        Context:\n        {{documents}}\n\n        Question: {{question}}\n\n        Answer the question using only the provided context. If the context does not contain enough information, say so.\n        ",
    )

    ChainOfThought = _usr(
        "Chain of Thought",
        "        {{question}}\n\n        Think step by step:\n        1. Identify the key components of the problem.\n        2. Break down the solution into logical steps.\n        3. Show your work at each step.\n        4. Arrive at the final answer.\n        ",
    )

    Compare = _usr(
        "Compare",
        "        Compare {{optionA}} vs {{optionB}} for {{useCase}}.\n\n        Consider: pros, cons, performance, ease of use, and when to choose each.\n        Present as a structured comparison.\n        ",
    )

    GenerateApiDocs = _usr(
        "Generate API Docs",
        "        Generate REST API documentation for the following endpoint:\n\n        {{endpoint}}\n\n        Include: HTTP method, URL, request/response body, status codes, headers, and example usage.\n        ",
    )

    CreateUserStory = _usr(
        "Create User Story",
        "        Create a user story for the following feature:\n\n        {{feature}}\n\n        Format:\n        As a {{persona}}, I want to [action] so that [benefit].\n\n        Include acceptance criteria as a checklist.\n        ",
    )

    AnalyzeSentiment = _usr(
        "Analyze Sentiment",
        "        Analyze the sentiment of the following text:\n\n        {{text}}\n\n        Provide: overall sentiment (positive/negative/neutral), confidence score, and key phrases that influenced the rating.\n        ",
    )

    GenerateCommitMessage = _usr(
        "Generate Commit Message",
        "        Generate a conventional commit message for the following diff:\n\n        {{diff}}\n\n        Follow conventional commits format: type(scope): description\n        Include a brief body if the change is complex.\n        ",
    )

    RefactorCode = _usr(
        "Refactor Code",
        "        Refactor the following {{language}} code to improve {{goal}}:\n\n        ```{{language}}\n        {{code}}\n        ```\n\n        Explain what you changed and why. Preserve existing behavior.\n        ",
    )

    CreateProjectPlan = _usr(
        "Create Project Plan",
        "        Create a project plan for:\n\n        {{requirements}}\n\n        Include: phases, tasks, estimated duration, dependencies, and milestones.\n        Target timeline: {{timeline}}.\n        ",
    )

    WriteBlogPost = _usr(
        "Write Blog Post",
        "        Write a technical blog post about {{topic}}.\n\n        Target audience: {{audience}}\n        Tone: {{tone}}\n        Length: approximately {{wordCount}} words.\n\n        Include: introduction, key sections, code examples where relevant, and a conclusion.\n        ",
    )

    GenerateTestCases = _usr(
        "Generate Test Cases",
        "        Generate test cases for the following requirement:\n\n        {{requirement}}\n\n        Include: test name, preconditions, steps, expected result, and priority (Critical/High/Medium/Low).\n        Cover: happy path, edge cases, negative scenarios, and boundary conditions.\n        ",
    )

    ExplainError = _usr(
        "Explain Error",
        "        Explain the following error and suggest how to fix it:\n\n        Error: {{error}}\n\n        Context:\n        ```{{language}}\n        {{code}}\n        ```\n\n        Explain: what caused it, why it happens, and how to prevent it in the future.\n        ",
    )

    DesignSchema = _usr(
        "Design Schema",
        "        Design a {{schemaType}} schema for:\n\n        {{requirements}}\n\n        Consider: relationships, constraints, indexing strategy, and normalization level.\n        Provide the schema definition and explain design decisions.\n        ",
    )

    GenerateRegex = _usr(
        "Generate Regex",
        "        Create a regex pattern that matches: {{description}}\n\n        Provide:\n        - The regex pattern\n        - Explanation of each part\n        - Example matches\n        - Example non-matches\n        ",
    )

    CreateAgenda = _usr(
        "Create Agenda",
        "        Create a meeting agenda for:\n\n        Meeting: {{meetingName}}\n        Duration: {{duration}}\n        Attendees: {{attendees}}\n        Topics: {{topics}}\n\n        Include time allocations, discussion points, and desired outcomes for each item.\n        ",
    )

    CodeReviewChecklist = _usr(
        "Code Review Checklist",
        "        Generate a code review checklist for a {{language}} {{projectType}} project.\n\n        Focus areas: {{focusAreas}}\n\n        Include categories: correctness, security, performance, maintainability, testing, documentation.\n        ",
    )

    SelfEvaluate = _usr(
        "Self Evaluate",
        "        Evaluate the following response for quality:\n\n        {{response}}\n\n        Score on a scale of 1-10 for:\n        - Accuracy\n        - Completeness\n        - Clarity\n        - Usefulness\n\n        Provide specific suggestions for improvement.\n        ",
    )

    ExtractStructuredData = _usr(
        "Extract Structured Data",
        "        Extract structured data from the following text:\n\n        {{text}}\n\n        Output format: {{format}}\n\n        Extract: {{fields}}\n        ",
    )
