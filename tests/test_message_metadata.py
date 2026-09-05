"""Port of MessageMetadataTests.cs."""

from datetime import datetime, timedelta, timezone

import pytest

from mima_ai_prompt import MessageMetadata, PromptVersion


def test_empty_has_all_null_or_default_properties():
    metadata = MessageMetadata.empty()
    assert metadata.name is None
    assert metadata.description is None
    assert metadata.category is None
    assert metadata.version is None
    assert metadata.author is None
    assert metadata.tags == []
    assert metadata.language is None
    assert metadata.provider is None
    assert metadata.model is None
    assert metadata.min_compatible_version is None
    assert metadata.semantic_version is None


def test_with_name_creates_metadata_with_only_name():
    metadata = MessageMetadata.with_name("MyName")
    assert metadata.name == "MyName"


def test_ctor_sets_all_provided_values():
    created = datetime.now(timezone.utc) - timedelta(days=1)
    modified = datetime.now(timezone.utc)
    metadata = MessageMetadata(
        name="n",
        description="d",
        category="c",
        version="1.0.0",
        author="a",
        tags=["t1", "t2"],
        language="en",
        provider="openai",
        model="gpt-4",
        created=created,
        modified=modified,
        min_compatible_version="0.9.0",
    )
    assert metadata.name == "n"
    assert metadata.description == "d"
    assert metadata.category == "c"
    assert metadata.version == "1.0.0"
    assert metadata.author == "a"
    assert metadata.tags == ["t1", "t2"]
    assert metadata.language == "en"
    assert metadata.provider == "openai"
    assert metadata.model == "gpt-4"
    assert metadata.created == created
    assert metadata.modified == modified
    assert metadata.min_compatible_version == "0.9.0"


def test_ctor_defaults_created_and_modified_to_utc_now():
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    metadata = MessageMetadata()
    after = datetime.now(timezone.utc) + timedelta(seconds=1)
    assert before <= metadata.created <= after
    assert before <= metadata.modified <= after


def test_set_name_returns_new_instance_with_updated_name():
    original = MessageMetadata.empty()
    updated = original.set_name("NewName")
    assert updated.name == "NewName"
    assert original.name is None


def test_set_description_returns_new_instance_with_updated_description():
    assert MessageMetadata.empty().set_description("desc").description == "desc"


def test_set_version_string_returns_new_instance_with_updated_version():
    assert MessageMetadata.empty().set_version("2.0.0").version == "2.0.0"


def test_set_version_prompt_version_returns_new_instance_with_version_string():
    assert (
        MessageMetadata.empty().set_version(PromptVersion.create(1, 2, 3)).version
        == "1.2.3"
    )


def test_set_version_null_prompt_version_throws():
    with pytest.raises(TypeError):
        MessageMetadata.empty().set_version(None)


def test_semantic_version_valid_version_string_returns_parsed_version():
    metadata = MessageMetadata.empty().set_version("1.2.3")
    assert metadata.semantic_version.major == 1


def test_semantic_version_invalid_version_string_returns_null():
    metadata = MessageMetadata.empty().set_version("not-a-version!!!")
    assert metadata.semantic_version is None


def test_semantic_version_no_version_set_returns_null():
    assert MessageMetadata.empty().semantic_version is None


def test_set_tags_returns_new_instance_with_tags():
    assert MessageMetadata.empty().set_tags(["a", "b"]).tags == ["a", "b"]


def test_add_tag_appends_to_existing_tags():
    metadata = MessageMetadata.empty().set_tags(["a"]).add_tag("b")
    assert metadata.tags == ["a", "b"]


def test_set_author_returns_new_instance_with_updated_author():
    assert MessageMetadata.empty().set_author("Jane").author == "Jane"


def test_set_category_returns_new_instance_with_updated_category():
    assert MessageMetadata.empty().set_category("coding").category == "coding"


def test_set_language_returns_new_instance_with_updated_language():
    assert MessageMetadata.empty().set_language("fr").language == "fr"


def test_set_provider_returns_new_instance_with_updated_provider():
    assert MessageMetadata.empty().set_provider("anthropic").provider == "anthropic"


def test_set_model_returns_new_instance_with_updated_model():
    assert MessageMetadata.empty().set_model("claude-3").model == "claude-3"


def test_set_min_compatible_version_string_returns_new_instance():
    assert (
        MessageMetadata.empty()
        .set_min_compatible_version("1.0.0")
        .min_compatible_version
        == "1.0.0"
    )


def test_set_min_compatible_version_prompt_version_returns_new_instance():
    assert (
        MessageMetadata.empty()
        .set_min_compatible_version(PromptVersion.create(1, 0, 0))
        .min_compatible_version
        == "1.0.0"
    )


def test_set_min_compatible_version_null_prompt_version_throws():
    with pytest.raises(TypeError):
        MessageMetadata.empty().set_min_compatible_version(None)


def test_fluent_chaining_produces_fully_configured_metadata():
    metadata = (
        MessageMetadata.empty()
        .set_name("Chain")
        .set_description("desc")
        .set_category("cat")
        .set_version("1.0.0")
        .set_author("author")
        .add_tag("tag1")
        .set_language("en")
        .set_provider("openai")
        .set_model("gpt-4")
        .set_min_compatible_version("0.5.0")
    )
    assert metadata.name == "Chain"
    assert metadata.description == "desc"
    assert metadata.category == "cat"
    assert metadata.version == "1.0.0"
    assert metadata.author == "author"
    assert "tag1" in metadata.tags
    assert metadata.language == "en"
    assert metadata.provider == "openai"
    assert metadata.model == "gpt-4"
    assert metadata.min_compatible_version == "0.5.0"
