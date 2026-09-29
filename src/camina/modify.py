"""Functions that modify stored data without changing the data type.

Contents:
    Adders:
        add_prefix (dispatcher): adds a str prefix to item.
        add_slots: adds `__slots__` to a dataclass.
        add_suffix (dispatcher): adds a str suffix to item.
    Dividers:
        cleave (dispatcher): divides an item into 2 parts based on `divider`.
        separate (dispatcher): divides an item into n+1 parts based on
            `divider`.
    Subtractors:
        deduplicate (dispatcher): removes duplicate data from an item.
        drop_dunders (dispatcher): drops strings (or names) that start and end
            with double underscores.
        drop_prefix (dispatcher): removes a str prefix from an item.
        drop_privates (dispatcher): drops strings (or names) that start with an
            underscore.
        drop_substring (dispatcher): removes a substring from an item.
        drop_suffix (dispatcher): removes a str suffix from an item.
    Other:
        capitalify: converts a snake case str to capital case.
        snakify: converts a capital case str to snake case.
        uniquify: returns a unique key for a dict.

Each dispatcher is a `functools.singledispatch` function. The functions that
handle specific types (for example, `add_prefix_to_str` or
`drop_suffix_from_list`) are registered with their dispatcher and can also be
called directly.

To Do:
    Add dispatched versions of the `drop_*` functions for nested data.

"""

from __future__ import annotations

import collections
import dataclasses
import functools
import re
from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Mapping,
    MutableSequence,
)
from collections.abc import Set as AbstractSet
from typing import Any, TypeVar

_CONTAINERS: tuple[type, ...] = (Mapping, MutableSequence, AbstractSet, tuple)
_UNSUPPORTED: str = "item is not a supported type for {name}"
_T = TypeVar("_T")


""" Private Helpers """


def _rebuild(original: _T, contents: Any) -> _T:
    """Returns `contents` as the same type as `original`, if possible.

    Args:
        original (_T): container whose type should be matched.
        contents (Any): new dict, list, set, or tuple with the data to return.

    Returns:
        Any: `contents` converted to the type of `original`. If `original`
            cannot be recreated from `contents`, `contents` is returned.

    """
    kind: Any = type(original)
    if kind is type(contents):
        return contents  # type: ignore[no-any-return]
    if isinstance(original, collections.defaultdict):
        return kind(original.default_factory, contents)  # type: ignore[no-any-return]
    try:
        return kind(contents)  # type: ignore[no-any-return]
    except TypeError:
        return contents  # type: ignore[no-any-return]


def _apply_to_names(
    item: _T, func: Callable[[str], str], recursive: bool = False
) -> _T:
    """Applies `func` to the str data in `item`.

    For a mapping, `func` is applied to the keys. For all other containers,
    `func` is applied to the items in the container.

    Args:
        item (_T): str, mapping, list, set, or tuple to modify.
        func (Callable[[str], str]): function that modifies a str.
        recursive (bool): whether to apply `func` to nested containers
            (including the values of mappings that are themselves containers).
            Defaults to False.

    Raises:
        TypeError: if `item` or a modified element is not a supported type.

    Returns:
        Any: modified version of `item`.

    """
    if isinstance(item, str):
        return func(item)  # type: ignore[return-value]
    if isinstance(item, Mapping):
        contents = {}
        for key, value in item.items():
            if recursive and isinstance(value, _CONTAINERS):
                value = _apply_to_names(value, func, recursive)  # noqa: PLW2901
            contents[_apply_to_names(key, func, recursive)] = value
        return _rebuild(item, contents)
    if isinstance(item, _CONTAINERS):
        elements = []
        for element in item:  # type: ignore[attr-defined]
            if isinstance(element, str) or recursive:
                elements.append(_apply_to_names(element, func, recursive))
            else:
                raise TypeError("items in item must be str types")
        if isinstance(item, AbstractSet):
            return _rebuild(item, set(elements))
        if isinstance(item, tuple):
            return tuple(elements)  # type: ignore[return-value]
        return _rebuild(item, elements)
    raise TypeError(_UNSUPPORTED.format(name=__name__))


def _name_of(thing: Any) -> str:
    """Returns the str `thing` or the `name`/`__name__` attribute of `thing`.

    Args:
        thing (Any): str or object with a `name` or `__name__` attribute.

    Raises:
        TypeError: if `thing` is not a str and has no str `name` or `__name__`.

    Returns:
        str: name of `thing`.

    """
    if isinstance(thing, str):
        return thing
    for attribute in ("name", "__name__"):
        name = getattr(thing, attribute, None)
        if isinstance(name, str):
            return name
    raise TypeError(
        "items in item must be str types or have name or __name__ attributes"
    )


def _drop_names(item: _T, drop: Callable[[str], bool]) -> _T:
    """Drops entries of `item` whose names satisfy `drop`.

    Args:
        item (_T): mapping, list, set, or tuple to modify. Mapping keys that are
            not str types are never dropped.
        drop (Callable[[str], bool]): function that returns True if a name
            should be dropped.

    Raises:
        TypeError: if `item` is not a mapping and includes items that are
            neither str types nor objects with `name` or `__name__` attributes.

    Returns:
        Any: modified version of `item`.

    """
    if isinstance(item, Mapping):
        contents = {
            k: v
            for k, v in item.items()
            if not (isinstance(k, str) and drop(k))
        }
        return _rebuild(item, contents)
    kept = [i for i in item if not drop(_name_of(i))]  # type: ignore[attr-defined]
    if isinstance(item, AbstractSet):
        return _rebuild(item, set(kept))
    if isinstance(item, tuple):
        return tuple(kept)  # type: ignore[return-value]
    return _rebuild(item, kept)


def _is_dunder(name: str) -> bool:
    """Returns whether `name` starts and ends with a double underscore."""
    return name.startswith("__") and name.endswith("__")


def _is_private(name: str) -> bool:
    """Returns whether `name` starts with an underscore."""
    return name.startswith("_")


""" Adders """


@functools.singledispatch
def add_prefix(
    item: Any,
    /,
    prefix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> Any:
    """Adds `prefix` to `item` with `divider` in between.

    Args:
        item (Any): item to be modified.
        prefix (str): prefix to be added to `item`.
        divider (str | None): str to add between `item` and `prefix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        Any: modified item.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


def _prefixer(prefix: str, divider: str | None) -> Callable[[str], str]:
    """Returns a function that adds `prefix` and `divider` to a str."""
    return lambda x: (divider or "").join((prefix, x))


@add_prefix.register(str)
def add_prefix_to_str(
    item: str,
    /,
    prefix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> str:
    """Adds `prefix` to `item` with `divider` in between.

    Args:
        item (str): item to be modified.
        prefix (str): prefix to be added to `item`.
        divider (str | None): str to add between `item` and `prefix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): has no effect because `item` is a str. It is
            included for a consistent interface. Defaults to False.

    Returns:
        str: modified str.

    """
    return _prefixer(prefix, divider)(item)


@add_prefix.register(Mapping)
def add_prefix_to_dict(
    item: Mapping[str, Any],
    /,
    prefix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> Mapping[str, Any]:
    """Adds `prefix` to keys in `item` with `divider` in between.

    Args:
        item (Mapping[str, Any]): item to be modified.
        prefix (str): prefix to be added to the keys of `item`.
        divider (str | None): str to add between a key and `prefix`. Defaults to
            "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    return _apply_to_names(item, _prefixer(prefix, divider), bool(recursive))


@add_prefix.register(MutableSequence)
def add_prefix_to_list(
    item: MutableSequence[str],
    /,
    prefix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> MutableSequence[str]:
    """Adds `prefix` to items in `item` with `divider` in between.

    Args:
        item (MutableSequence[str]): item to be modified.
        prefix (str): prefix to be added to the items of `item`.
        divider (str | None): str to add between an item and `prefix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        MutableSequence[str]: modified mutable sequence.

    """
    return _apply_to_names(item, _prefixer(prefix, divider), bool(recursive))


@add_prefix.register(AbstractSet)
def add_prefix_to_set(
    item: AbstractSet[str],
    /,
    prefix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> AbstractSet[str]:
    """Adds `prefix` to items in `item` with `divider` in between.

    Args:
        item (AbstractSet[str]): item to be modified.
        prefix (str): prefix to be added to the items of `item`.
        divider (str | None): str to add between an item and `prefix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        AbstractSet[str]: modified set.

    """
    return _apply_to_names(item, _prefixer(prefix, divider), bool(recursive))


@add_prefix.register(tuple)
def add_prefix_to_tuple(
    item: tuple[str, ...],
    /,
    prefix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> tuple[str, ...]:
    """Adds `prefix` to items in `item` with `divider` in between.

    Args:
        item (tuple[str, ...]): item to be modified.
        prefix (str): prefix to be added to the items of `item`.
        divider (str | None): str to add between an item and `prefix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return _apply_to_names(item, _prefixer(prefix, divider), bool(recursive))


def add_slots(item: type[Any]) -> type[Any]:
    """Adds slots to dataclass with default values.

    Derived from code here:
    https://gitquirks.com/ericvsmith/dataclasses/blob/master/dataclass_tools.py

    Because a new class is created, methods that use the zero-argument form of
    `super()` will not work in the returned class.

    Args:
        item (type[Any]): dataclass to add slots to.

    Raises:
        TypeError: if `__slots__` is already in `item` or `item` is not a
            dataclass.

    Returns:
        type[Any]: class with `__slots__` added.

    """
    if "__slots__" in item.__dict__:
        raise TypeError(f"{item.__name__} already contains __slots__")
    item_dict = dict(item.__dict__)
    field_names = tuple(f.name for f in dataclasses.fields(item))
    item_dict["__slots__"] = field_names
    for field_name in field_names:
        item_dict.pop(field_name, None)
    item_dict.pop("__dict__", None)
    item_dict.pop("__weakref__", None)
    metaclass: Any = type(item)
    new_item: type[Any] = metaclass(item.__name__, item.__bases__, item_dict)
    new_item.__qualname__ = item.__qualname__
    return new_item


@functools.singledispatch
def add_suffix(
    item: Any,
    /,
    suffix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> Any:
    """Adds `suffix` to `item` with `divider` in between.

    Args:
        item (Any): item to be modified.
        suffix (str): suffix to be added to `item`.
        divider (str | None): str to add between `item` and `suffix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        Any: modified item.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


def _suffixer(suffix: str, divider: str | None) -> Callable[[str], str]:
    """Returns a function that adds `suffix` and `divider` to a str."""
    return lambda x: (divider or "").join((x, suffix))


@add_suffix.register(str)
def add_suffix_to_str(
    item: str,
    /,
    suffix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> str:
    """Adds `suffix` to `item` with `divider` in between.

    Args:
        item (str): item to be modified.
        suffix (str): suffix to be added to `item`.
        divider (str | None): str to add between `item` and `suffix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): has no effect because `item` is a str. It is
            included for a consistent interface. Defaults to False.

    Returns:
        str: modified str.

    """
    return _suffixer(suffix, divider)(item)


@add_suffix.register(Mapping)
def add_suffix_to_dict(
    item: Mapping[str, Any],
    /,
    suffix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> Mapping[str, Any]:
    """Adds `suffix` to keys in `item` with `divider` in between.

    Args:
        item (Mapping[str, Any]): item to be modified.
        suffix (str): suffix to be added to the keys of `item`.
        divider (str | None): str to add between a key and `suffix`. Defaults to
            "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    return _apply_to_names(item, _suffixer(suffix, divider), bool(recursive))


@add_suffix.register(MutableSequence)
def add_suffix_to_list(
    item: MutableSequence[str],
    /,
    suffix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> MutableSequence[str]:
    """Adds `suffix` to items in `item` with `divider` in between.

    Args:
        item (MutableSequence[str]): item to be modified.
        suffix (str): suffix to be added to the items of `item`.
        divider (str | None): str to add between an item and `suffix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        MutableSequence[str]: modified mutable sequence.

    """
    return _apply_to_names(item, _suffixer(suffix, divider), bool(recursive))


@add_suffix.register(AbstractSet)
def add_suffix_to_set(
    item: AbstractSet[str],
    /,
    suffix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> AbstractSet[str]:
    """Adds `suffix` to items in `item` with `divider` in between.

    Args:
        item (AbstractSet[str]): item to be modified.
        suffix (str): suffix to be added to the items of `item`.
        divider (str | None): str to add between an item and `suffix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        AbstractSet[str]: modified set.

    """
    return _apply_to_names(item, _suffixer(suffix, divider), bool(recursive))


@add_suffix.register(tuple)
def add_suffix_to_tuple(
    item: tuple[str, ...],
    /,
    suffix: str,
    divider: str | None = "",
    recursive: bool | None = False,
) -> tuple[str, ...]:
    """Adds `suffix` to items in `item` with `divider` in between.

    Args:
        item (tuple[str, ...]): item to be modified.
        suffix (str): suffix to be added to the items of `item`.
        divider (str | None): str to add between an item and `suffix`. Defaults
            to "", which means no divider will be added.
        recursive (bool | None): if `item` is nested, whether to apply the
            function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return _apply_to_names(item, _suffixer(suffix, divider), bool(recursive))


""" Dividers """


@functools.singledispatch
def cleave(
    item: Any,
    /,
    divider: Any,
    return_last: bool = True,
    raise_error: bool = False,
) -> tuple[Any, Any]:
    """Divides `item` into 2 parts based on `divider`.

    Args:
        item (Any): item to be divided.
        divider (Any): item to divide `item` upon.
        return_last (bool): whether to split `item` upon the last (True) or
            first (False) appearance of `divider`. Defaults to True.
        raise_error (bool): whether to raise an error if `divider` is not in
            `item` (True) or to return a tuple containing `item` twice (False).
            Defaults to False.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        tuple[Any, Any]: parts of `item` on either side of `divider` unless
            `divider` is not in `item`.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


@cleave.register(str)
def cleave_str(
    item: str,
    /,
    divider: str = "_",
    return_last: bool = True,
    raise_error: bool = False,
) -> tuple[str, str]:
    """Divides `item` into 2 parts based on `divider`.

    Args:
        item (str): item to be divided.
        divider (str): item to divide `item` upon. Defaults to "_".
        return_last (bool): whether to split `item` upon the last (True) or
            first (False) appearance of `divider`. Defaults to True.
        raise_error (bool): whether to raise an error if `divider` is not in
            `item` (True) or to return a tuple containing `item` twice (False).
            Defaults to False.

    Raises:
        ValueError: if `divider` is not in `item` and `raise_error` is True.

    Returns:
        tuple[str, str]: parts of `item` on either side of `divider` unless
            `divider` is not in `item`.

    """
    if divider in item:
        if return_last:
            prefix, _, suffix = item.rpartition(divider)
        else:
            prefix, _, suffix = item.partition(divider)
        return prefix, suffix
    if raise_error:
        raise ValueError(f"{divider} is not in {item}")
    return item, item


@functools.singledispatch
def separate(
    item: Any, /, divider: Any, raise_error: bool = False
) -> list[Any]:
    """Divides `item` into n+1 parts based on `divider`.

    Args:
        item (Any): item to be divided.
        divider (Any): item to divide `item` upon.
        raise_error (bool): whether to raise an error if `divider` is not in
            `item` (True) or to return a list containing `item` (False).
            Defaults to False.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        list[Any]: parts of `item` on either side of `divider` unless
            `divider` is not in `item`.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


@separate.register(str)
def separate_str(
    item: str, /, divider: str = "_", raise_error: bool = False
) -> list[str]:
    """Divides `item` into n+1 parts based on `divider`.

    Args:
        item (str): item to be divided.
        divider (str): item to divide `item` upon. Defaults to "_".
        raise_error (bool): whether to raise an error if `divider` is not in
            `item` (True) or to return a list containing `item` (False).
            Defaults to False.

    Raises:
        ValueError: if `divider` is not in `item` and `raise_error` is True.

    Returns:
        list[str]: parts of `item` on either side of `divider` unless `divider`
            is not in `item`.

    """
    if divider in item:
        return item.split(divider)
    if raise_error:
        raise ValueError(f"{divider} is not in {item}")
    return [item]


""" Subtractors """


@functools.singledispatch
def deduplicate(item: Any, /) -> Any:
    """Deduplicates contents of `item`.

    The first appearance of each element is kept and order is preserved.

    Args:
        item (Any): item to deduplicate.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        Any: deduplicated item.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


def _unique(items: Iterable[Any]) -> list[Any]:
    """Returns unique elements of `items` in order of first appearance.

    Args:
        items (Iterable[Any]): iterable that may include unhashable elements.

    Returns:
        list[Any]: elements without duplicates.

    """
    seen: dict[Hashable, None] = {}
    unhashable: list[Any] = []
    result: list[Any] = []
    for element in items:
        try:
            if element in seen:
                continue
            seen[element] = None
        except TypeError:
            if element in unhashable:
                continue
            unhashable.append(element)
        result.append(element)
    return result


@deduplicate.register(MutableSequence)
def deduplicate_list(item: MutableSequence[Any], /) -> MutableSequence[Any]:
    """Deduplicates contents of `item`.

    Args:
        item (MutableSequence[Any]): item to deduplicate.

    Returns:
        MutableSequence[Any]: deduplicated item.

    """
    return _rebuild(item, _unique(item))


@deduplicate.register(tuple)
def deduplicate_tuple(item: tuple[Any, ...], /) -> tuple[Any, ...]:
    """Deduplicates contents of `item`.

    Args:
        item (tuple[Any, ...]): item to deduplicate.

    Returns:
        tuple[Any, ...]: deduplicated item.

    """
    return tuple(_unique(item))


@functools.singledispatch
def drop_dunders(item: Any, /) -> Any:
    """Drops items in `item` that start and end with a double underscore.

    Args:
        item (Any): item to modify.

    Raises:
        TypeError: if `item` is not a registered type.

    Returns:
        Any: item with entries dropped that start and end with a double
            underscore.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


@drop_dunders.register(Mapping)
def drop_dunders_dict(item: Mapping[str, Any], /) -> Mapping[str, Any]:
    """Drops items in `item` with key names that are dunders.

    Args:
        item (Mapping[str, Any]): dict-like object with str keys that might be
            dunder names.

    Returns:
        Mapping[str, Any]: dict-like object with entries dropped if the key name
            starts and ends with a double underscore.

    """
    return _drop_names(item, _is_dunder)


@drop_dunders.register(MutableSequence)
def drop_dunders_list(
    item: MutableSequence[str | object], /
) -> MutableSequence[str | object]:
    """Drops items in `item` with names that are dunders.

    Args:
        item (MutableSequence[str | object]): list-like object with str items or
            items with names that might be dunders.

    Raises:
        TypeError: if `item` does not contain str types or objects with either
            `name` or `__name__` attributes.

    Returns:
        MutableSequence[str | object]: list-like object with items dropped if
            they or their names start and end with a double underscore.

    """
    return _drop_names(item, _is_dunder)


@drop_dunders.register(AbstractSet)
def drop_dunders_set(
    item: AbstractSet[str | object], /
) -> AbstractSet[str | object]:
    """Drops items in `item` with names that are dunders.

    Args:
        item (AbstractSet[str | object]): set-like object with str items or
            items with names that might be dunders.

    Raises:
        TypeError: if `item` does not contain str types or objects with either
            `name` or `__name__` attributes.

    Returns:
        AbstractSet[str | object]: set-like object with items dropped if they or
            their names start and end with a double underscore.

    """
    return _drop_names(item, _is_dunder)


@drop_dunders.register(tuple)
def drop_dunders_tuple(item: tuple[str | object, ...], /) -> tuple[Any, ...]:
    """Drops items in `item` with names that are dunders.

    Args:
        item (tuple[str | object, ...]): tuple with str items or items with
            names that might be dunders.

    Raises:
        TypeError: if `item` does not contain str types or objects with either
            `name` or `__name__` attributes.

    Returns:
        tuple[str | object, ...]: tuple with items dropped if they or their
            names start and end with a double underscore.

    """
    return _drop_names(item, _is_dunder)


@functools.singledispatch
def drop_prefix(item: Any, /, prefix: str, divider: str = "") -> Any:
    """Drops `prefix` from `item` with `divider` in between.

    Args:
        item (Any): item to be modified.
        prefix (str): prefix to be dropped from `item`.
        divider (str): str between `prefix` and the rest of `item`, which is
            dropped with `prefix`. Defaults to "", which means no divider is
            expected.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        Any: modified item.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


def _prefix_dropper(prefix: str, divider: str) -> Callable[[str], str]:
    """Returns a function that removes `prefix` and `divider` from a str."""
    full_prefix = f"{prefix}{divider}"
    return lambda x: x.removeprefix(full_prefix)


@drop_prefix.register(str)
def drop_prefix_from_str(item: str, /, prefix: str, divider: str = "") -> str:
    """Drops `prefix` from `item` with `divider` in between.

    Args:
        item (str): item to be modified.
        prefix (str): prefix to be dropped from `item`.
        divider (str): str between `prefix` and the rest of `item`, which is
            dropped with `prefix`. Defaults to "", which means no divider is
            expected.

    Returns:
        str: modified str.

    """
    return _prefix_dropper(prefix, divider)(item)


@drop_prefix.register(Mapping)
def drop_prefix_from_dict(
    item: Mapping[str, Any], /, prefix: str, divider: str = ""
) -> Mapping[str, Any]:
    """Drops `prefix` from keys in `item` with `divider` in between.

    Args:
        item (Mapping[str, Any]): item to be modified.
        prefix (str): prefix to be dropped from the keys of `item`.
        divider (str): str between `prefix` and the rest of a key, which is
            dropped with `prefix`. Defaults to "", which means no divider is
            expected.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    return _apply_to_names(item, _prefix_dropper(prefix, divider))


@drop_prefix.register(MutableSequence)
def drop_prefix_from_list(
    item: MutableSequence[str], /, prefix: str, divider: str = ""
) -> MutableSequence[str]:
    """Drops `prefix` from items in `item` with `divider` in between.

    Args:
        item (MutableSequence[str]): item to be modified.
        prefix (str): prefix to be dropped from the items of `item`.
        divider (str): str between `prefix` and the rest of an item, which is
            dropped with `prefix`. Defaults to "", which means no divider is
            expected.

    Returns:
        MutableSequence[str]: modified sequence.

    """
    return _apply_to_names(item, _prefix_dropper(prefix, divider))


@drop_prefix.register(AbstractSet)
def drop_prefix_from_set(
    item: AbstractSet[str], /, prefix: str, divider: str = ""
) -> AbstractSet[str]:
    """Drops `prefix` from items in `item` with `divider` in between.

    Args:
        item (AbstractSet[str]): item to be modified.
        prefix (str): prefix to be dropped from the items of `item`.
        divider (str): str between `prefix` and the rest of an item, which is
            dropped with `prefix`. Defaults to "", which means no divider is
            expected.

    Returns:
        AbstractSet[str]: modified set.

    """
    return _apply_to_names(item, _prefix_dropper(prefix, divider))


@drop_prefix.register(tuple)
def drop_prefix_from_tuple(
    item: tuple[str, ...], /, prefix: str, divider: str = ""
) -> tuple[str, ...]:
    """Drops `prefix` from items in `item` with `divider` in between.

    Args:
        item (tuple[str, ...]): item to be modified.
        prefix (str): prefix to be dropped from the items of `item`.
        divider (str): str between `prefix` and the rest of an item, which is
            dropped with `prefix`. Defaults to "", which means no divider is
            expected.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return _apply_to_names(item, _prefix_dropper(prefix, divider))


@functools.singledispatch
def drop_privates(item: Any, /) -> Any:
    """Drops items in `item` with names beginning with an underscore.

    Args:
        item (Any): item to modify.

    Raises:
        TypeError: if `item` is not a registered type.

    Returns:
        Any: item with entries dropped beginning with an underscore.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


@drop_privates.register(Mapping)
def drop_privates_dict(item: Mapping[str, Any], /) -> Mapping[str, Any]:
    """Drops items in `item` with key names beginning with an underscore.

    Args:
        item (Mapping[str, Any]): dict-like object with str keys that might have
            underscores at the beginning of the key names.

    Returns:
        Mapping[str, Any]: dict-like object with entries dropped if the key name
            begins with an underscore.

    """
    return _drop_names(item, _is_private)


@drop_privates.register(MutableSequence)
def drop_privates_list(
    item: MutableSequence[str | object], /
) -> MutableSequence[str | object]:
    """Drops items in `item` with names beginning with an underscore.

    Args:
        item (MutableSequence[str | object]): list-like object with str items or
            items with names that might have underscores at their beginnings.

    Raises:
        TypeError: if `item` does not contain str types or objects with either
            `name` or `__name__` attributes.

    Returns:
        MutableSequence[str | object]: list-like object with items dropped if
            they or their names begin with an underscore.

    """
    return _drop_names(item, _is_private)


@drop_privates.register(AbstractSet)
def drop_privates_set(
    item: AbstractSet[str | object], /
) -> AbstractSet[str | object]:
    """Drops items in `item` with names beginning with an underscore.

    Args:
        item (AbstractSet[str | object]): set-like object with str items or
            items with names that might have underscores at their beginnings.

    Raises:
        TypeError: if `item` does not contain str types or objects with either
            `name` or `__name__` attributes.

    Returns:
        AbstractSet[str | object]: set-like object with items dropped if they or
            their names begin with an underscore.

    """
    return _drop_names(item, _is_private)


@drop_privates.register(tuple)
def drop_privates_tuple(item: tuple[str | object, ...], /) -> tuple[Any, ...]:
    """Drops items in `item` with names beginning with an underscore.

    Args:
        item (tuple[str | object, ...]): tuple with str items or items with
            names that might have underscores at their beginnings.

    Raises:
        TypeError: if `item` does not contain str types or objects with either
            `name` or `__name__` attributes.

    Returns:
        tuple[str | object, ...]: tuple with items dropped if they or their
            names begin with an underscore.

    """
    return _drop_names(item, _is_private)


@functools.singledispatch
def drop_substring(item: Any, /, substring: str) -> Any:
    """Drops `substring` from `item`.

    Args:
        item (Any): item to be modified.
        substring (str): substring to be dropped from `item`.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        Any: modified item.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


@drop_substring.register(str)
def drop_substring_from_str(item: str, /, substring: str) -> str:
    """Drops `substring` from `item`.

    Args:
        item (str): item to be modified.
        substring (str): substring to be dropped from `item`.

    Returns:
        str: modified str.

    """
    return item.replace(substring, "")


@drop_substring.register(Mapping)
def drop_substring_from_dict(
    item: Mapping[str, Any], /, substring: str
) -> Mapping[str, Any]:
    """Drops `substring` from keys in `item`.

    Args:
        item (Mapping[str, Any]): item to be modified.
        substring (str): substring to be dropped from the keys of `item`.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    return _apply_to_names(item, lambda x: x.replace(substring, ""))


@drop_substring.register(MutableSequence)
def drop_substring_from_list(
    item: MutableSequence[str], /, substring: str
) -> MutableSequence[str]:
    """Drops `substring` from items in `item`.

    Args:
        item (MutableSequence[str]): item to be modified.
        substring (str): substring to be dropped from the items of `item`.

    Returns:
        MutableSequence[str]: modified sequence.

    """
    return _apply_to_names(item, lambda x: x.replace(substring, ""))


@drop_substring.register(AbstractSet)
def drop_substring_from_set(
    item: AbstractSet[str], /, substring: str
) -> AbstractSet[str]:
    """Drops `substring` from items in `item`.

    Args:
        item (AbstractSet[str]): item to be modified.
        substring (str): substring to be dropped from the items of `item`.

    Returns:
        AbstractSet[str]: modified set.

    """
    return _apply_to_names(item, lambda x: x.replace(substring, ""))


@drop_substring.register(tuple)
def drop_substring_from_tuple(
    item: tuple[str, ...], /, substring: str
) -> tuple[str, ...]:
    """Drops `substring` from items in `item`.

    Args:
        item (tuple[str, ...]): item to be modified.
        substring (str): substring to be dropped from the items of `item`.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return _apply_to_names(item, lambda x: x.replace(substring, ""))


@functools.singledispatch
def drop_suffix(item: Any, /, suffix: str, divider: str = "") -> Any:
    """Drops `suffix` from `item` with `divider` in between.

    Args:
        item (Any): item to be modified.
        suffix (str): suffix to be dropped from `item`.
        divider (str): str between the rest of `item` and `suffix`, which is
            dropped with `suffix`. Defaults to "", which means no divider is
            expected.

    Raises:
        TypeError: if no registered function supports the type of `item`.

    Returns:
        Any: modified item.

    """
    raise TypeError(_UNSUPPORTED.format(name=__name__))


def _suffix_dropper(suffix: str, divider: str) -> Callable[[str], str]:
    """Returns a function that removes `divider` and `suffix` from a str."""
    full_suffix = f"{divider}{suffix}"
    return lambda x: x.removesuffix(full_suffix)


@drop_suffix.register(str)
def drop_suffix_from_str(item: str, /, suffix: str, divider: str = "") -> str:
    """Drops `suffix` from `item` with `divider` in between.

    Args:
        item (str): item to be modified.
        suffix (str): suffix to be dropped from `item`.
        divider (str): str between the rest of `item` and `suffix`, which is
            dropped with `suffix`. Defaults to "", which means no divider is
            expected.

    Returns:
        str: modified str.

    """
    return _suffix_dropper(suffix, divider)(item)


@drop_suffix.register(Mapping)
def drop_suffix_from_dict(
    item: Mapping[str, Any], /, suffix: str, divider: str = ""
) -> Mapping[str, Any]:
    """Drops `suffix` from keys in `item` with `divider` in between.

    Args:
        item (Mapping[str, Any]): item to be modified.
        suffix (str): suffix to be dropped from the keys of `item`.
        divider (str): str between the rest of a key and `suffix`, which is
            dropped with `suffix`. Defaults to "", which means no divider is
            expected.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    return _apply_to_names(item, _suffix_dropper(suffix, divider))


@drop_suffix.register(MutableSequence)
def drop_suffix_from_list(
    item: MutableSequence[str], /, suffix: str, divider: str = ""
) -> MutableSequence[str]:
    """Drops `suffix` from items in `item` with `divider` in between.

    Args:
        item (MutableSequence[str]): item to be modified.
        suffix (str): suffix to be dropped from the items of `item`.
        divider (str): str between the rest of an item and `suffix`, which is
            dropped with `suffix`. Defaults to "", which means no divider is
            expected.

    Returns:
        MutableSequence[str]: modified sequence.

    """
    return _apply_to_names(item, _suffix_dropper(suffix, divider))


@drop_suffix.register(AbstractSet)
def drop_suffix_from_set(
    item: AbstractSet[str], /, suffix: str, divider: str = ""
) -> AbstractSet[str]:
    """Drops `suffix` from items in `item` with `divider` in between.

    Args:
        item (AbstractSet[str]): item to be modified.
        suffix (str): suffix to be dropped from the items of `item`.
        divider (str): str between the rest of an item and `suffix`, which is
            dropped with `suffix`. Defaults to "", which means no divider is
            expected.

    Returns:
        AbstractSet[str]: modified set.

    """
    return _apply_to_names(item, _suffix_dropper(suffix, divider))


@drop_suffix.register(tuple)
def drop_suffix_from_tuple(
    item: tuple[str, ...], /, suffix: str, divider: str = ""
) -> tuple[str, ...]:
    """Drops `suffix` from items in `item` with `divider` in between.

    Args:
        item (tuple[str, ...]): item to be modified.
        suffix (str): suffix to be dropped from the items of `item`.
        divider (str): str between the rest of an item and `suffix`, which is
            dropped with `suffix`. Defaults to "", which means no divider is
            expected.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return _apply_to_names(item, _suffix_dropper(suffix, divider))


""" Other Modifiers """


def capitalify(item: str) -> str:
    """Converts a snake case str to capital case.

    Args:
        item (str): str to convert.

    Returns:
        str: `item` converted to capital case.

    """
    return item.replace("_", " ").title().replace(" ", "")


def snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): str to convert.

    Returns:
        str: `item` converted to snake case.

    """
    item = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", item)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", item).lower()


def uniquify(
    key: str, dictionary: Mapping[Hashable, Any], index: int | None = 1
) -> str:
    """Creates a unique key name to avoid overwriting an item in `dictionary`.

    The function is 1-indexed so that the first attempt to avoid a duplicate
    will be: "old_name2".

    Args:
        key (str): name of key to test.
        dictionary (Mapping[Hashable, Any]): dict for which a unique key name is
            sought.
        index (int | None): number from which to start counting. The first
            suffix tried is `index` + 1. Defaults to 1.

    Returns:
        str: unique key name for `dictionary`.

    """
    if key not in dictionary:
        return key
    counter = 1 if index is None else index
    while True:
        counter += 1
        name = f"{key}{counter}"
        if name not in dictionary:
            return name
