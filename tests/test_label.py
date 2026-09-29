"""Tests for `camina.label`."""

from __future__ import annotations

import dataclasses

import pytest

import camina


class SnakeCaseMe:
    """Class without a name attribute."""


@dataclasses.dataclass
class Named:
    name: str = "chosen"


def test_namify_str() -> None:
    assert camina.namify("already") == "already"


def test_namify_instance_with_name() -> None:
    assert camina.namify(Named()) == "chosen"


def test_namify_classes_and_functions() -> None:
    assert camina.namify(SnakeCaseMe) == "snake_case_me"
    assert camina.namify(Named) == "named"
    assert camina.namify(test_namify_str) == "test_namify_str"


def test_namify_instance_without_name() -> None:
    assert camina.namify(SnakeCaseMe()) == "snake_case_me"
    assert camina.namify(3) == "int"


def test_namify_ignores_non_str_name() -> None:
    thing = SnakeCaseMe()
    thing.name = 5  # type: ignore[attr-defined]
    assert camina.namify(thing) == "snake_case_me"


def test_namify_default() -> None:
    class Nameless:
        __name__ = ""

    assert camina.namify(Nameless(), default="fallback") == "fallback"
    assert camina.namify(Nameless()) is None


@pytest.mark.parametrize(
    ("item", "expected"), [("Word", "Word"), (Named(), "chosen")]
)
def test_namify_parametrized(item: object, expected: str) -> None:
    assert camina.namify(item) == expected
