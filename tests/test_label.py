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


class TestName:
    def test_inferred_and_stored(self) -> None:
        class Owner:
            name = camina.Name()

        owner = Owner()
        assert owner.name == "owner"
        owner.name = "stored"
        assert owner.name == "stored"
        assert owner._name == "stored"  # type: ignore[attr-defined]

    def test_class_access(self) -> None:
        class Owner:
            name = camina.Name()

        assert isinstance(Owner.name, camina.Name)

    def test_custom_namer(self) -> None:
        class Owner:
            name = camina.Name(namer=lambda x: f"custom_{x.__name__}")

        assert Owner().name == "custom_Owner"

    def test_in_dataclass(self) -> None:
        @dataclasses.dataclass
        class Owner:
            name: str = camina.Name()  # type: ignore[assignment]
            other: int = 1

        assert Owner().name == "owner"
        assert Owner(name="given").name == "given"
        assert camina.namify(Owner()) == "owner"

    def test_global_namer_is_used(self) -> None:
        class Owner:
            name = camina.Name()

        camina.set_key_namer(lambda x: "global")
        try:
            assert Owner().name == "global"
        finally:
            camina.set_key_namer(None)

    def test_method_namer_default(self) -> None:
        assert camina.get_method_namer()(SnakeCaseMe) == "from_snake_case_me"


@pytest.mark.parametrize(
    ("item", "expected"), [("Word", "Word"), (Named(), "chosen")]
)
def test_namify_parametrized(item: object, expected: str) -> None:
    assert camina.namify(item) == expected
