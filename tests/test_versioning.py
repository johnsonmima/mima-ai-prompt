"""Port of VersioningTests.cs."""

from datetime import datetime, timedelta, timezone

import pytest

from mima_ai_prompt import (
    PromptBuilder,
    PromptVersion,
    PromptVersionHistory,
    VersionedPromptAsset,
)


def _make_prompt(content: str):
    return PromptBuilder.user_only(content)


def test_create_sets_name_version_and_content():
    prompt = _make_prompt("v1")
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), prompt
    )
    assert asset.name == "MyAsset"
    assert asset.version == PromptVersion.create(1, 0, 0)
    assert asset.content is prompt
    assert asset.id
    assert asset.is_deprecated is False


@pytest.mark.parametrize("name", [None, "", "   "])
def test_create_empty_name_throws(name):
    with pytest.raises(ValueError, match="Asset name cannot be null or empty"):
        VersionedPromptAsset.create(
            name, PromptVersion.create(1, 0, 0), _make_prompt("v1")
        )


def test_create_null_version_throws():
    with pytest.raises(TypeError):
        VersionedPromptAsset.create("MyAsset", None, _make_prompt("v1"))


def test_create_null_content_throws():
    with pytest.raises(TypeError):
        VersionedPromptAsset.create("MyAsset", PromptVersion.create(1, 0, 0), None)


def test_with_description_sets_description():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    ).with_description("desc")
    assert asset.description == "desc"


def test_with_author_sets_author():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    ).with_author("Jane")
    assert asset.author == "Jane"


def test_with_tags_sets_tags():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    ).with_tags("a", "b")
    assert asset.tags == ["a", "b"]


def test_with_change_log_sets_change_log():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    ).with_change_log("Initial release")
    assert asset.change_log == "Initial release"


def test_deprecate_marks_as_deprecated_with_reason():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    ).deprecate("Use v2 instead")
    assert asset.is_deprecated
    assert asset.deprecation_message == "Use v2 instead"


def test_bump_major_creates_new_version_with_new_id():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 5, 3), _make_prompt("v1")
    ).with_author("Jane").with_description("desc").with_tags("a")
    bumped = asset.bump_major(_make_prompt("v2"), "Breaking change note")
    assert bumped.version == PromptVersion.create(2, 0, 0)
    assert bumped.id != asset.id
    assert bumped.change_log == "Breaking change note"
    assert bumped.author == "Jane"
    assert bumped.description == "desc"
    assert bumped.tags == ["a"]


def test_bump_major_default_change_log_when_not_provided():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    )
    assert asset.bump_major(_make_prompt("v2")).change_log == "Breaking change"


def test_bump_minor_creates_new_version():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 5, 3), _make_prompt("v1")
    )
    bumped = asset.bump_minor(_make_prompt("v2"))
    assert bumped.version == PromptVersion.create(1, 6, 0)
    assert bumped.change_log == "New feature"


def test_bump_patch_creates_new_version():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 5, 3), _make_prompt("v1")
    )
    bumped = asset.bump_patch(_make_prompt("v2"))
    assert bumped.version == PromptVersion.create(1, 5, 4)
    assert bumped.change_log == "Bug fix"


def test_to_string_includes_name_and_version():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    )
    assert str(asset) == "MyAsset v1.0.0"


def test_to_string_deprecated_includes_deprecated_tag():
    asset = VersionedPromptAsset.create(
        "MyAsset", PromptVersion.create(1, 0, 0), _make_prompt("v1")
    ).deprecate("old")
    assert str(asset) == "MyAsset v1.0.0 [DEPRECATED]"


def test_history_create_sets_asset_name():
    history = PromptVersionHistory.create("SupportBot")
    assert history.asset_name == "SupportBot"
    assert history.count == 0
    assert history.latest is None
    assert history.latest_stable is None


@pytest.mark.parametrize("name", [None, "", "   "])
def test_history_create_empty_asset_name_throws(name):
    with pytest.raises(ValueError, match="Asset name cannot be null or empty"):
        PromptVersionHistory.create(name)


def test_add_adds_version_entry():
    history = PromptVersionHistory.create("SupportBot")
    history.add(
        PromptVersion.create(1, 0, 0), _make_prompt("v1"), "Initial release", "Jane"
    )
    assert history.count == 1
    entry = history.get(PromptVersion.create(1, 0, 0))
    assert entry.change_log == "Initial release"
    assert entry.author == "Jane"


def test_add_null_version_throws():
    history = PromptVersionHistory.create("SupportBot")
    with pytest.raises(TypeError):
        history.add(None, _make_prompt("v1"))


def test_add_null_content_throws():
    history = PromptVersionHistory.create("SupportBot")
    with pytest.raises(TypeError):
        history.add(PromptVersion.create(1, 0, 0), None)


def test_add_duplicate_version_throws():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    with pytest.raises(RuntimeError, match="already exists"):
        history.add(PromptVersion.create(1, 0, 0), _make_prompt("v2"))


def test_get_unknown_version_returns_null():
    history = PromptVersionHistory.create("SupportBot")
    assert history.get(PromptVersion.create(9, 9, 9)) is None


def test_get_content_returns_content_for_version():
    prompt = _make_prompt("v1")
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), prompt)
    assert history.get_content(PromptVersion.create(1, 0, 0)) is prompt


def test_get_content_unknown_version_returns_null():
    history = PromptVersionHistory.create("SupportBot")
    assert history.get_content(PromptVersion.create(1, 0, 0)) is None


def test_contains_existing_version_returns_true():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    assert history.contains(PromptVersion.create(1, 0, 0))
    assert not history.contains(PromptVersion.create(2, 0, 0))


def test_latest_returns_highest_version():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    history.add(PromptVersion.create(2, 0, 0), _make_prompt("v2"))
    history.add(PromptVersion.create(1, 5, 0), _make_prompt("v1.5"))
    assert history.latest.version == PromptVersion.create(2, 0, 0)


def test_latest_stable_ignores_pre_release_versions():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    history.add(PromptVersion.create(2, 0, 0, "beta"), _make_prompt("v2-beta"))
    assert history.latest_stable.version == PromptVersion.create(1, 0, 0)
    assert history.latest.version == PromptVersion.create(2, 0, 0, "beta")


def test_get_range_returns_inclusive_range():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    history.add(PromptVersion.create(1, 1, 0), _make_prompt("v1.1"))
    history.add(PromptVersion.create(2, 0, 0), _make_prompt("v2"))
    range_ = history.get_range(
        PromptVersion.create(1, 0, 0), PromptVersion.create(1, 1, 0)
    )
    assert len(range_) == 2


def test_get_change_log_returns_formatted_entries():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"), "Initial release")
    history.add(
        PromptVersion.create(1, 1, 0), _make_prompt("v1.1"), "Added tone parameter"
    )
    changelog = history.get_change_log(
        PromptVersion.create(1, 0, 0), PromptVersion.create(1, 1, 0)
    )
    assert len(changelog) == 2
    assert "v1.0.0" in changelog[0] and "Initial release" in changelog[0]
    assert "v1.1.0" in changelog[1] and "Added tone parameter" in changelog[1]


def test_get_change_log_skips_entries_without_change_log():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    history.add(PromptVersion.create(1, 1, 0), _make_prompt("v1.1"), "Added feature")
    changelog = history.get_change_log(
        PromptVersion.create(1, 0, 0), PromptVersion.create(1, 1, 0)
    )
    assert len(changelog) == 1


def test_all_returns_all_versions_in_ascending_order():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(2, 0, 0), _make_prompt("v2"))
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    assert len(history.all) == 2
    assert history.all[0].version == PromptVersion.create(1, 0, 0)
    assert history.all[1].version == PromptVersion.create(2, 0, 0)


def test_version_entry_to_string_includes_version_and_date():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"), "Initial release")
    entry = history.get(PromptVersion.create(1, 0, 0))
    assert "v1.0.0" in str(entry) and "Initial release" in str(entry)


def test_version_entry_to_string_no_change_log_omits_colon():
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    entry = history.get(PromptVersion.create(1, 0, 0))
    assert ":" not in str(entry)


def test_version_entry_timestamp_is_set_on_creation():
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    history = PromptVersionHistory.create("SupportBot")
    history.add(PromptVersion.create(1, 0, 0), _make_prompt("v1"))
    after = datetime.now(timezone.utc) + timedelta(seconds=1)
    entry = history.get(PromptVersion.create(1, 0, 0))
    assert before <= entry.timestamp <= after
