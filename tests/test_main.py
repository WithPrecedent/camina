"""Main file for unit tests."""

from __future__ import annotations

import pathlib
import re

import pytest

import camina

ROOT = pathlib.Path(__file__).parent.parent


def test_version_matches_pyproject() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf8")
    match = re.search(r'^version = "([^"]+)"', text, flags=re.MULTILINE)
    assert match is not None
    assert camina.__version__ == match.group(1)


def test_metadata() -> None:
    assert camina.__author__ == "Corey Rayburn Yung"
    assert camina.__doc__


def test_all_is_complete_and_unique() -> None:
    assert len(camina.__all__) == len(set(camina.__all__))
    for name in camina.__all__:
        assert hasattr(camina, name), name


@pytest.mark.parametrize("name", camina.__all__)
def test_exports_are_documented(name: str) -> None:
    assert getattr(camina, name).__doc__, name


def test_public_names_are_exported() -> None:
    """Checks that public functions and classes in modules are exported."""
    modules = [camina.clock, camina.label, camina.modify]
    for module in modules:
        for name, value in vars(module).items():
            defined_here = getattr(value, "__module__", None) == module.__name__
            if defined_here and not name.startswith("_"):
                assert name in camina.__all__, f"{module.__name__}.{name}"
