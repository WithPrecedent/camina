"""Tests for `camina.base`."""

from __future__ import annotations

import copy
import dataclasses
from typing import Any

import pytest

import camina
from camina import base


@dataclasses.dataclass
class Wrapped:
    """Simple class to wrap in a Proxy."""

    name: str = "something"


@dataclasses.dataclass
class SimpleBunch(camina.Bunch):
    """Minimal concrete Bunch."""

    contents: list[Any] = dataclasses.field(default_factory=list)

    def add(self, item: Any) -> None:
        self.contents.append(item)

    def delete(self, item: Any) -> None:
        self.contents.remove(item)

    def subset(self, include: Any = None, exclude: Any = None) -> SimpleBunch:
        return SimpleBunch([i for i in self.contents if i != exclude])


class TestResolveDefault:
    def test_value(self) -> None:
        assert base.resolve_default("Nada") == "Nada"
        assert base.resolve_default(None) is None

    def test_callable(self) -> None:
        assert base.resolve_default(list) == []
        assert base.resolve_default(lambda: 5) == 5


class TestBunch:
    def test_abstract(self) -> None:
        with pytest.raises(TypeError):
            camina.Bunch(contents=[])  # type: ignore[abstract]

    def test_add_returns_new_object(self) -> None:
        bunch = SimpleBunch([1, 2])
        result = bunch + 3
        assert result.contents == [1, 2, 3]
        assert bunch.contents == [1, 2]
        assert result is not bunch

    def test_iadd_changes_in_place(self) -> None:
        bunch = SimpleBunch([1, 2])
        original = bunch
        bunch += 3
        assert bunch is original
        assert bunch.contents == [1, 2, 3]

    def test_delitem_contains_iter_len(self) -> None:
        bunch = SimpleBunch([1, 2, 3])
        del bunch[2]
        assert bunch.contents == [1, 3]
        assert 3 in bunch
        assert 2 not in bunch
        assert list(bunch) == [1, 3]
        assert len(bunch) == 2

    def test_delitem_missing(self) -> None:
        with pytest.raises(ValueError, match="not in list"):
            del SimpleBunch([1])[5]


class TestDescriptor:
    def test_set_name_and_storage(self) -> None:
        class Owner:
            value = camina.Descriptor()

        descriptor = Owner.__dict__["value"]
        assert descriptor.attribute_name == "value"
        assert descriptor.private_name == "_value"
        assert descriptor.owner is Owner
        owner = Owner()
        owner.value = 7
        assert owner.value == 7
        assert owner._value == 7  # type: ignore[attr-defined]

    def test_class_access_returns_descriptor(self) -> None:
        class Owner:
            value = camina.Descriptor()

        assert isinstance(Owner.value, camina.Descriptor)

    def test_unset_raises(self) -> None:
        class Owner:
            value = camina.Descriptor()

        with pytest.raises(AttributeError):
            _ = Owner().value


class TestProxy:
    def test_attribute_access_and_setting(self) -> None:
        wrapped = Wrapped()
        proxy = camina.Proxy(contents=wrapped)
        proxy.id = 4543
        assert proxy.name == "something"
        assert proxy.id == 4543
        assert hasattr(proxy, "id")
        assert wrapped.id == 4543  # type: ignore[attr-defined]
        del proxy.id
        assert not hasattr(proxy, "id")
        assert not hasattr(wrapped, "id")

    def test_existing_wrapped_attribute_is_set_on_wrapped(self) -> None:
        wrapped = Wrapped()
        proxy = camina.Proxy(contents=wrapped)
        proxy.name = "changed"
        assert wrapped.name == "changed"

    def test_proxy_attribute_is_set_on_proxy(self) -> None:
        proxy = camina.Proxy(contents=Wrapped())
        proxy.contents = Wrapped("other")
        assert proxy.name == "other"

    def test_attribute_falls_back_to_proxy(self) -> None:
        proxy = camina.Proxy(contents=[1, 2])
        proxy.extra = "x"  # a list does not accept new attributes
        assert proxy.extra == "x"
        assert "extra" in proxy.__dict__
        del proxy.extra
        assert not hasattr(proxy, "extra")

    def test_none_contents(self) -> None:
        proxy = camina.Proxy()
        proxy.extra = 1
        assert proxy.extra == 1
        with pytest.raises(AttributeError):
            _ = proxy.missing

    def test_missing_attribute(self) -> None:
        proxy = camina.Proxy(contents=Wrapped())
        with pytest.raises(AttributeError):
            _ = proxy.missing
        with pytest.raises(AttributeError):
            del proxy.missing

    def test_dunder_attributes_are_not_forwarded(self) -> None:
        class HasDunder:
            __custom__ = 1

        proxy = camina.Proxy(contents=HasDunder())
        assert not hasattr(proxy, "__custom__")

    def test_contains(self) -> None:
        assert "a" in camina.Proxy(contents=["a", "b"])
        assert "c" not in camina.Proxy(contents=["a", "b"])
        wrapped = Wrapped()
        assert wrapped in camina.Proxy(contents=wrapped)
        assert 5 in camina.Proxy(contents=5)
        assert 6 not in camina.Proxy(contents=5)
        assert None in camina.Proxy()

    def test_container_methods(self) -> None:
        proxy = camina.Proxy(contents=[1, 2, 3])
        assert proxy[1] == 2
        proxy[1] = 5
        assert proxy.contents == [1, 5, 3]
        del proxy[0]
        assert list(proxy) == [5, 3]
        assert len(proxy) == 2
        assert proxy.count(3) == 1

    def test_call(self) -> None:
        assert camina.Proxy(contents=lambda x, y=1: x + y)(2, y=3) == 5

    def test_truthiness(self) -> None:
        assert camina.Proxy(contents=[])
        assert camina.Proxy()

    def test_copy(self) -> None:
        proxy = camina.Proxy(contents=Wrapped("a"))
        clone = copy.deepcopy(proxy)
        assert clone == proxy
        assert clone.contents is not proxy.contents
