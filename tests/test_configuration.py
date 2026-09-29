"""Tests for `camina.configuration`."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import camina
from camina import configuration


@pytest.fixture(autouse=True)
def _reset_namers() -> Iterator[None]:
    yield
    camina.set_key_namer(None)
    camina.set_method_namer(None)


def test_wildcards() -> None:
    assert "all" in configuration._ALL_KEYS
    assert "default" in configuration._DEFAULT_KEYS
    assert "none" in configuration._NONE_KEYS


def test_missing_sentinel() -> None:
    assert configuration._MISSING is not None
    assert configuration._MISSING == configuration._MISSING_VALUE()


def test_set_key_namer() -> None:
    assert camina.get_key_namer() is camina.namify
    camina.set_key_namer(lambda x: "custom")
    assert camina.get_key_namer()(object()) == "custom"
    camina.set_key_namer(None)
    assert camina.get_key_namer() is camina.namify


def test_set_method_namer() -> None:
    assert camina.get_method_namer()("Thing") == "from_Thing"
    camina.set_method_namer(lambda x: f"make_{x}")
    assert camina.get_method_namer()("a") == "make_a"
    camina.set_method_namer(None)
    assert camina.get_method_namer()(int) == "from_int"


def test_namers_must_be_callable() -> None:
    with pytest.raises(TypeError):
        camina.set_key_namer("not callable")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        camina.set_method_namer(5)  # type: ignore[arg-type]


def test_key_namer_used_by_repository() -> None:
    camina.set_key_namer(lambda x: "same")
    repository = camina.Repository()
    repository.add(1)
    repository.add(2)
    assert list(repository.keys()) == ["same", "same2"]
