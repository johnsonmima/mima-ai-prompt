"""Package identity: PyPI name vs import name, version, typing marker."""

import re
from importlib.metadata import metadata
from pathlib import Path

import mima_ai_prompt


def _pyproject_text() -> str:
    return (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
        encoding="utf-8"
    )


def test_import_module_is_underscored():
    assert mima_ai_prompt.__name__ == "mima_ai_prompt"


def test_dunder_version_matches_pyproject():
    match = re.search(r'(?m)^version = "([^"]+)"', _pyproject_text())
    assert match is not None
    assert mima_ai_prompt.__version__ == match.group(1)


def test_pypi_name_is_hyphenated():
    match = re.search(r'(?m)^name = "([^"]+)"', _pyproject_text())
    assert match is not None
    assert match.group(1) == "mima-ai-prompt"


def test_py_typed_marker_is_shipped():
    pkg = Path(mima_ai_prompt.__file__).resolve().parent
    assert (pkg / "py.typed").is_file()


def test_distribution_name_when_installed():
    dist = metadata("mima-ai-prompt")
    assert dist["Name"] == "mima-ai-prompt"
