"""Tests that the README is accurate and its examples work."""

from __future__ import annotations

import doctest
import pathlib
import re

import pytest

import camina

README = pathlib.Path(__file__).parent.parent / "README.md"
TEXT = README.read_text(encoding="utf8")
BLOCKS = re.findall(r"```pycon\n(.*?)```", TEXT, flags=re.DOTALL)


def test_readme_has_no_placeholders() -> None:
    assert "TODO" not in TEXT
    assert "[summary]" not in TEXT


def test_readme_examples_run() -> None:
    """Runs every `pycon` block in the README as one doctest session."""
    assert len(BLOCKS) >= 3
    parser = doctest.DocTestParser()
    runner = doctest.DocTestRunner(
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    )
    namespace: dict[str, object] = {}
    failures = []
    for number, block in enumerate(BLOCKS):
        test = parser.get_doctest(block, namespace, f"README-{number}", None, 0)
        runner.run(test, out=failures.append, clear_globs=False)
        namespace.update(test.globs)
    assert not failures, "".join(failures)
    assert runner.summarize(verbose=False).attempted > 30


def _listed_names() -> list[str]:
    """Returns the names in backticks that start bullet points."""
    return re.findall(r"^\s*\* `(\w+)`", TEXT, flags=re.MULTILINE)


@pytest.mark.parametrize("name", sorted(set(_listed_names())))
def test_documented_names_exist(name: str) -> None:
    assert hasattr(camina, name) or hasattr(camina.convert, name)


@pytest.mark.parametrize("name", camina.__all__)
def test_exported_names_are_documented(name: str) -> None:
    assert f"`{name}`" in TEXT
