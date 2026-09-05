"""Port of PromptVersionTests.cs."""

import pytest

from mima_ai_prompt import PromptVersion


def test_create_sets_components():
    version = PromptVersion.create(1, 2, 3)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3


def test_create_defaults_minor_and_patch_to_zero():
    version = PromptVersion.create(1)
    assert version.minor == 0
    assert version.patch == 0


def test_initial_is_one_zero_zero():
    version = PromptVersion.initial()
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0
    assert version.is_stable is True


@pytest.mark.parametrize("major,minor,patch", [(-1, 0, 0), (0, -1, 0), (0, 0, -1)])
def test_ctor_negative_component_throws(major, minor, patch):
    with pytest.raises(ValueError):
        PromptVersion(major, minor, patch)


def test_parse_full_version_parses_all_components():
    version = PromptVersion.parse("1.2.3")
    assert (version.major, version.minor, version.patch) == (1, 2, 3)
    assert version.pre_release is None
    assert version.build_metadata is None


def test_parse_major_only_defaults_minor_and_patch():
    version = PromptVersion.parse("5")
    assert (version.major, version.minor, version.patch) == (5, 0, 0)


def test_parse_major_minor_defaults_patch():
    version = PromptVersion.parse("2.3")
    assert (version.major, version.minor, version.patch) == (2, 3, 0)


def test_parse_with_pre_release_parses_pre_release():
    version = PromptVersion.parse("1.2.3-beta")
    assert version.pre_release == "beta"
    assert version.is_pre_release
    assert version.is_stable is False


def test_parse_with_build_metadata_parses_build_metadata():
    version = PromptVersion.parse("1.0.0+build.123")
    assert version.build_metadata == "build.123"
    assert version.pre_release is None


def test_parse_with_pre_release_and_build_metadata_parses_both():
    version = PromptVersion.parse("1.0.0-rc.1+build.456")
    assert version.pre_release == "rc.1"
    assert version.build_metadata == "build.456"
    assert version.major == 1


def test_parse_trims_whitespace():
    assert PromptVersion.parse("  1.0.0  ").major == 1


@pytest.mark.parametrize("input_value", [None, "", "   "])
def test_parse_null_or_empty_throws(input_value):
    with pytest.raises(ValueError, match="Version string cannot be null or empty"):
        PromptVersion.parse(input_value)


def test_parse_too_many_parts_throws():
    with pytest.raises(ValueError, match="Invalid version format"):
        PromptVersion.parse("1.2.3.4")


def test_parse_invalid_major_throws():
    with pytest.raises(ValueError, match="Invalid major version"):
        PromptVersion.parse("abc.2.3")


def test_parse_invalid_minor_throws():
    with pytest.raises(ValueError, match="Invalid minor version"):
        PromptVersion.parse("1.abc.3")


def test_try_parse_valid_returns_version():
    version = PromptVersion.try_parse("1.0.0")
    assert version is not None


def test_try_parse_invalid_returns_none():
    assert PromptVersion.try_parse("1.2.3.4") is None


def test_try_parse_null_or_empty_returns_none():
    assert PromptVersion.try_parse(None) is None
    assert PromptVersion.try_parse("") is None


def test_next_major_increments_major_and_resets_others():
    version = PromptVersion.create(1, 5, 3).next_major()
    assert (version.major, version.minor, version.patch) == (2, 0, 0)


def test_next_minor_increments_minor_and_resets_patch():
    version = PromptVersion.create(1, 5, 3).next_minor()
    assert (version.major, version.minor, version.patch) == (1, 6, 0)


def test_next_patch_increments_patch_only():
    version = PromptVersion.create(1, 5, 3).next_patch()
    assert (version.major, version.minor, version.patch) == (1, 5, 4)


def test_with_pre_release_sets_pre_release_label():
    version = PromptVersion.create(1, 0, 0).with_pre_release("beta")
    assert version.pre_release == "beta"
    assert version.is_pre_release


def test_with_build_metadata_sets_build_metadata():
    version = PromptVersion.create(1, 0, 0).with_build_metadata("sha.123")
    assert version.build_metadata == "sha.123"


def test_to_stable_strips_pre_release_and_build_metadata():
    version = PromptVersion.parse("1.2.3-beta+build.1").to_stable()
    assert version.pre_release is None
    assert version.build_metadata is None
    assert str(version) == "1.2.3"


def test_is_compatible_with_same_major_higher_minor_returns_true():
    assert PromptVersion.create(1, 2, 0).is_compatible_with(
        PromptVersion.create(1, 1, 0)
    )


def test_is_compatible_with_same_major_minor_higher_patch_returns_true():
    assert PromptVersion.create(1, 1, 5).is_compatible_with(
        PromptVersion.create(1, 1, 2)
    )


def test_is_compatible_with_different_major_returns_false():
    assert not PromptVersion.create(2, 0, 0).is_compatible_with(
        PromptVersion.create(1, 0, 0)
    )


def test_is_compatible_with_lower_minor_returns_false():
    assert not PromptVersion.create(1, 0, 0).is_compatible_with(
        PromptVersion.create(1, 1, 0)
    )


def test_is_compatible_with_null_returns_false():
    assert not PromptVersion.create(1, 0, 0).is_compatible_with(None)


def test_compare_to_null_returns_positive():
    assert PromptVersion.create(1, 0, 0)._cmp(None) > 0


def test_compare_to_higher_major_returns_negative():
    assert PromptVersion.create(1, 0, 0)._cmp(PromptVersion.create(2, 0, 0)) < 0


def test_compare_to_higher_minor_returns_negative():
    assert PromptVersion.create(1, 0, 0)._cmp(PromptVersion.create(1, 1, 0)) < 0


def test_compare_to_higher_patch_returns_negative():
    assert PromptVersion.create(1, 0, 0)._cmp(PromptVersion.create(1, 0, 1)) < 0


def test_compare_to_pre_release_vs_stable_pre_release_is_lower():
    stable = PromptVersion.create(1, 0, 0)
    pre_release = PromptVersion.create(1, 0, 0, "beta")
    assert pre_release._cmp(stable) < 0
    assert stable._cmp(pre_release) > 0


def test_compare_to_both_pre_release_compares_labels_ordinally():
    alpha = PromptVersion.create(1, 0, 0, "alpha")
    beta = PromptVersion.create(1, 0, 0, "beta")
    assert alpha._cmp(beta) < 0


def test_compare_to_equal_returns_zero():
    assert PromptVersion.create(1, 2, 3)._cmp(PromptVersion.create(1, 2, 3)) == 0


def test_equals_same_major_minor_patch_and_pre_release_returns_true():
    v1 = PromptVersion.create(1, 0, 0, "beta")
    v2 = PromptVersion.create(1, 0, 0, "beta")
    assert v1 == v2


def test_equals_different_pre_release_returns_false():
    assert PromptVersion.create(1, 0, 0, "beta") != PromptVersion.create(
        1, 0, 0, "alpha"
    )


def test_equals_null_returns_false():
    v1 = PromptVersion.create(1, 0, 0)
    assert v1 != None
    assert v1 != "1.0.0"


def test_get_hash_code_equal_versions_have_same_hash_code():
    v1 = PromptVersion.create(1, 2, 3, "beta")
    v2 = PromptVersion.create(1, 2, 3, "beta")
    assert hash(v1) == hash(v2)


def test_to_string_full_version_formats_correctly():
    assert str(PromptVersion(1, 2, 3, "beta", "build.1")) == "1.2.3-beta+build.1"


def test_to_string_simple_version_formats_correctly():
    assert str(PromptVersion.create(1, 0, 0)) == "1.0.0"


def test_equality_operator_works():
    v1 = PromptVersion.create(1, 0, 0)
    v2 = PromptVersion.create(1, 0, 0)
    v3 = PromptVersion.create(2, 0, 0)
    assert v1 == v2
    assert v1 != v3


def test_comparison_operators_work():
    lower = PromptVersion.create(1, 0, 0)
    lower_copy = PromptVersion.create(1, 0, 0)
    higher = PromptVersion.create(2, 0, 0)
    higher_copy = PromptVersion.create(2, 0, 0)
    assert lower < higher
    assert higher > lower
    assert lower <= lower_copy
    assert higher >= higher_copy
    assert lower <= higher
    assert higher >= lower
