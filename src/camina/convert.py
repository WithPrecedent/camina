"""Functions that convert types.

Contents:
    General Converters:
        dictify (dispatcher): converts to or validates a dict.
        hashify (dispatcher): converts to or validates a hashable object.
        instancify: converts to or validates an instance. If it is already an
            instance, any passed kwargs are added as attributes to the
            instance.
        integerify (dispatcher): converts to or validates an int.
        iterify: converts to or validates an iterable.
        kwargify: uses annotations to turn positional arguments into keyword
            arguments.
        listify (dispatcher): converts to or validates a list.
        numify (dispatcher): converts to or validates a numerical type.
        pathlibify (dispatcher): converts to or validates a pathlib.Path.
        stringify (dispatcher): converts to or validates a str.
        tuplify (dispatcher): converts to or validates a tuple.
        typify: converts a str type to other common types, if possible.
        windowify: returns a sliding window of `length` over `item`.
    Specific Converters:
        to_dict (dispatcher): converts an item to a dict.
        to_index (dispatcher): converts an item to an int usable as an index.
        str_to_index
        to_int (dispatcher): converts an item to an int.
        str_to_int
        float_to_int
        to_list (dispatcher): converts an item to a list.
        str_to_list
        to_float (dispatcher): converts an item to a float.
        int_to_float
        str_to_float
        to_path (dispatcher): converts an item to a pathlib.Path.
        str_to_path
        to_str (dispatcher): converts an item to a str.
        int_to_str
        float_to_str
        list_to_str
        none_to_str
        path_to_str
        datetime_to_str

The `namify` function, which returns a str name for an item, is in
`camina.label` and is exported in the top-level `camina` namespace.

Each dispatcher is a `functools.singledispatch` function. The functions that
handle specific types are registered with their dispatcher and can also be
called directly.

To Do:
    Add more flexible tools.

"""

from __future__ import annotations

import ast
import collections
import dataclasses
import datetime
import functools
import inspect
import itertools
import operator
import pathlib
from collections.abc import (
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from collections.abc import Set as AbstractSet
from typing import Any, cast

_NULL_STRINGS: tuple[str, ...] = ("None", "none")
_UNSUPPORTED: str = (
    "item cannot be converted because it is an unsupported type: {name}"
)


""" Private Helpers """


def _is_collection(item: Any) -> bool:
    """Returns whether `item` is an iterable that should be converted.

    Strings, bytes, and mappings are treated as single items and not as
    collections of items.

    Args:
        item (Any): item to check.

    Returns:
        bool: whether `item` is a non-str, non-bytes, non-mapping iterable.

    """
    return isinstance(item, Iterable) and not isinstance(
        item, (str, bytes, bytearray, Mapping)
    )


def _null_default(default: Any, empty: Any) -> Any:
    """Returns the value to use in place of a `None` item.

    Args:
        default (Any): default argument passed to a converter. None means that
            `empty` should be returned and the strings "None" or "none" mean
            that None should be returned.
        empty (Any): value to return if `default` is None.

    Returns:
        Any: value to return for a `None` item.

    """
    if default is None:
        return empty
    if isinstance(default, str) and default in _NULL_STRINGS:
        return None
    return default


""" General Converters """


@functools.singledispatch
def dictify(item: Any, /) -> MutableMapping[Hashable, Any]:
    """Converts `item` to a MutableMapping.

    Mutable mappings are returned as is. Other mappings and iterables of
    key/value pairs are converted to a dict.

    Args:
        item (Any): item to convert to a MutableMapping.

    Raises:
        TypeError: if `item` cannot be converted.

    Returns:
        MutableMapping[Hashable, Any]: derived from `item`.

    """
    if isinstance(item, MutableMapping):
        return item
    if isinstance(item, Mapping):
        return dict(item)
    if _is_collection(item):
        try:
            return dict(item)
        except (TypeError, ValueError):
            pass
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


@functools.singledispatch
def hashify(item: Any, /) -> Hashable:
    """Converts `item` to a Hashable.

    If `item` is hashable, it is returned as is. Otherwise, mappings, sets,
    and other collections are converted to hashable equivalents (tuples of
    items or frozensets) and any remaining unhashable objects are converted to
    a str.

    Args:
        item (Any): item to convert to a Hashable.

    Returns:
        Hashable: derived from `item`.

    """
    try:
        hash(item)
    except TypeError:
        if isinstance(item, Mapping):
            return tuple((hashify(k), hashify(v)) for k, v in item.items())
        if isinstance(item, AbstractSet):
            return frozenset(hashify(i) for i in item)
        if _is_collection(item):
            return tuple(hashify(i) for i in item)
        return str(item)
    return cast("Hashable", item)


def instancify(item: type[Any] | object, **kwargs: Any) -> Any:
    """Returns `item` as an instance with `kwargs` as parameters/attributes.

    If `item` is already an instance, kwargs are added as attributes to the
    existing `item`. This will overwrite any existing attributes of the same
    name.

    Args:
        item (type[Any] | object): class to make an instance out of by passing
            kwargs or an instance to add kwargs to as attributes.
        **kwargs (Any): keyword arguments to pass to `item` if it is a class or
            to add as attributes if it is an instance.

    Returns:
        Any: a class instance with `kwargs` as attributes or passed as
            parameters (if `item` is a class).

    """
    if inspect.isclass(item):
        return item(**kwargs)
    for key, value in kwargs.items():
        setattr(item, key, value)
    return item


@functools.singledispatch
def integerify(item: Any, /) -> int:
    """Converts `item` to an int.

    Args:
        item (Any): item to convert.

    Raises:
        TypeError: if `item` is a type that cannot be converted.

    Returns:
        int: derived from `item`.

    """
    if isinstance(item, int):
        return item
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


def iterify(item: Any, /) -> Iterable[Any]:
    """Returns `item` as an iterable, but does not iterate str types.

    Args:
        item (Any): item to turn into an iterable.

    Returns:
        Iterable[Any]: `item` if it is an iterable other than a str or bytes. A
            str or bytes type is stored as a single item in a tuple, a non-
            iterable is stored as a single item in a tuple, and None becomes an
            empty tuple.

    """
    if item is None:
        return ()
    if isinstance(item, (str, bytes, bytearray)):
        return (item,)
    if isinstance(item, Iterable):
        return item
    return (item,)


def kwargify(item: type[Any], /, args: tuple[Any, ...]) -> dict[str, Any]:
    """Converts `args` to kwargs using the annotations of `item`.

    For dataclasses, the names of the fields that are arguments to `__init__`
    are used. For other classes, the annotations of the class and its parents
    are used.

    Args:
        item (type[Any]): class with annotations used to construct kwargs.
        args (tuple[Any, ...]): arguments without keywords passed to `item`.

    Raises:
        ValueError: if there are more args than annotations in `item`.

    Returns:
        dict[str, Any]: kwargs based on `args` and `item`.

    """
    if dataclasses.is_dataclass(item):
        names = [f.name for f in dataclasses.fields(item) if f.init]
    else:
        annotations: dict[str, Any] = {}
        for base in reversed(inspect.getmro(item)):
            annotations.update(inspect.get_annotations(base))
        names = list(annotations)
    if len(args) > len(names):
        raise ValueError("There are too many args for item")
    return dict(zip(names, args, strict=False))


@functools.singledispatch
def listify(item: Any, /, default: Any | None = None) -> Any:
    """Returns passed item as a list (if not already a list).

    Args:
        item (Any): item to be transformed into a list to allow proper
            iteration. Non-str iterables (other than mappings) are converted to
            a list. All other items are wrapped in a list.
        default (Any | None): the default value to return if `item` is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put `"None"` in quotes. If not passed, `default` is set
            to [].

    Returns:
        Any: a passed list, `item` converted to a list, or the `default`
            argument.

    """
    if item is None:
        return _null_default(default, [])
    if isinstance(item, MutableSequence) and not isinstance(
        item, (str, bytearray)
    ):
        return item
    if _is_collection(item):
        return list(item)
    return [item]


@functools.singledispatch
def numify(item: Any, raise_error: bool = False) -> int | float | Any:
    """Converts `item` to a numeric type.

    If `item` cannot be converted to a numeric type and `raise_error` is False,
    `item` is returned as is.

    Args:
        item (Any): item to be converted.
        raise_error (bool): whether to raise a TypeError when conversion to a
            numeric type fails (True) or to simply return `item` (False).
            Defaults to False.

    Raises:
        TypeError: if `item` cannot be converted to a numeric type and
            `raise_error` is True.

    Returns:
        int | float | Any: converted to numeric type, if possible.

    """
    if isinstance(item, (int, float)):
        return item
    try:
        return int(item)
    except (TypeError, ValueError):
        try:
            return float(item)
        except (TypeError, ValueError):
            if raise_error:
                raise TypeError(
                    f"{item} not able to be converted to a numeric type"
                ) from None
            return item


@functools.singledispatch
def pathlibify(item: str | pathlib.Path, /) -> pathlib.Path:
    """Converts string `item` to pathlib.Path object.

    Args:
        item (str | pathlib.Path): either a string summary of a path or a
            pathlib.Path object.

    Raises:
        TypeError: if `item` is neither a str nor pathlib.Path type.

    Returns:
        pathlib.Path: `item` as a pathlib.Path.

    """
    if isinstance(item, pathlib.Path):
        return item
    raise TypeError("item must be str or pathlib.Path type")


@functools.singledispatch
def stringify(item: Any, /, default: Any | None = None) -> Any:
    """Converts `item` to a str from a Sequence.

    Args:
        item (Any): item to convert to a str from a list if it is a list.
        default (Any | None): value to return if `item` is None. To indicate you
            want None to be returned, use `"None"` in quotes. If not passed,
            `default` is set to "".

    Raises:
        TypeError: if `item` is not a str or list-like object.

    Returns:
        Any: str, if item was a sequence, the default value if None was passed,
            or the item as it was passed if it was already a str.

    """
    if item is None:
        return _null_default(default, "")
    if isinstance(item, str):
        return item
    if isinstance(item, Sequence) and not isinstance(item, (bytes, bytearray)):
        return ", ".join(str(i) for i in item)
    raise TypeError("item must be str or a sequence")


@functools.singledispatch
def tuplify(item: Any, /, default: Any | None = None) -> Any:
    """Returns passed item as a tuple (if not already a tuple).

    Args:
        item (Any): item to be transformed into a tuple. Non-str iterables
            (other than mappings) are converted to a tuple. All other items are
            wrapped in a tuple.
        default (Any | None): the default value to return if `item` is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put `"None"` in quotes. If not passed, `default` is set
            to ().

    Returns:
        Any: a passed tuple, `item` converted to a tuple, or `default`.

    """
    if item is None:
        return _null_default(default, ())
    if isinstance(item, tuple):
        return item
    if _is_collection(item):
        return tuple(item)
    return (item,)


def typify(item: Any) -> Any:
    """Converts strings to appropriate, supported datatypes.

    The method converts strings to list (if ', ' is present), int, float,
    or bool datatypes based upon the content of the string. If no
    alternative datatype is found, the item is returned in its original
    form.

    Args:
        item (Any): string to be converted to appropriate datatype. Other types
            are returned as is.

    Returns:
        Any: converted item.

    """
    if not isinstance(item, str):
        return item
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            if item.lower() in ("true", "yes"):
                return True
            if item.lower() in ("false", "no"):
                return False
            if ", " in item:
                return [typify(i) for i in item.split(", ")]
            return item


def windowify(
    item: Iterable[Any],
    length: int,
    fill_value: Any | None = None,
    step: int = 1,
) -> Iterator[tuple[Any, ...]]:
    """Returns a sliding window of `length` over `item`.

    This code is adapted from more_itertools.windowed to remove a dependency.

    Args:
        item (Iterable[Any]): iterable from which to return windows.
        length (int): length of window.
        fill_value (Any | None): value to use for items in a window that do not
            exist when length > len(item). Defaults to None.
        step (int): number of items to advance between each window. Defaults to
            1.

    Raises:
        ValueError: if `length` is less than 0 or `step` is less than 1.

    Returns:
        Iterator[tuple[Any, ...]]: windowed iterator derived from arguments.

    """
    if length < 0:
        raise ValueError("length must be >= 0")
    if length > 0 and step < 1:
        raise ValueError("step must be >= 1")
    return _windows(item, length, fill_value, step)


def _windows(
    item: Iterable[Any], length: int, fill_value: Any, step: int
) -> Iterator[tuple[Any, ...]]:
    """Yields the windows for `windowify` after its arguments are validated."""
    if length == 0:
        yield ()
        return
    window: collections.deque[Any] = collections.deque(maxlen=length)
    counter = length
    for _ in map(window.append, item):
        counter -= 1
        if not counter:
            counter = step
            yield tuple(window)
    size = len(window)
    if size < length:
        yield tuple(
            itertools.chain(window, itertools.repeat(fill_value, length - size))
        )
    elif 0 < counter < min(step, length):
        window += (fill_value,) * counter
        yield tuple(window)


""" Specific Converters """


@integerify.register(float)
def float_to_int(item: float, /) -> int:
    """Converts `item` to an int.

    Args:
        item (float): item to convert.

    Returns:
        int: derived from `item`. Any fractional part is truncated.

    """
    return int(item)


@integerify.register(str)
def str_to_int(item: str, /) -> int:
    """Converts `item` to an int.

    Args:
        item (str): item to convert.

    Raises:
        ValueError: if `item` is not a valid representation of an int.

    Returns:
        int: derived from `item`.

    """
    return int(item)


@functools.singledispatch
def to_int(item: Any, /) -> int:
    """Converts `item` to an int.

    Args:
        item (Any): item to convert to an int.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        int: derived from `item`.

    """
    if isinstance(item, int):
        return item
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


to_int.register(float, float_to_int)
to_int.register(str, str_to_int)


@functools.singledispatch
def to_index(item: Any, /) -> int:
    """Converts `item` to an int that can be used as an index.

    Args:
        item (Any): item to convert to an index. Anything that implements
            `__index__` is supported.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        int: derived from `item`.

    """
    try:
        return operator.index(item)
    except TypeError:
        raise TypeError(_UNSUPPORTED.format(name=type(item).__name__)) from None


@to_index.register(str)
def str_to_index(item: str, /) -> int:
    """Converts a str to an int that can be used as an index.

    Args:
        item (str): item to convert to an index.

    Raises:
        ValueError: if `item` is not a valid representation of an int.

    Returns:
        int: derived from `item`.

    """
    return int(item)


@to_index.register(float)
def _float_to_index(item: float, /) -> int:
    """Converts a float with an integer value to an index.

    Args:
        item (float): item to convert to an index.

    Raises:
        ValueError: if `item` is not a whole number.

    Returns:
        int: derived from `item`.

    """
    if not float(item).is_integer():
        raise ValueError(f"{item} is not a whole number")
    return int(item)


@functools.singledispatch
def to_dict(item: Any, /) -> dict[Hashable, Any]:
    """Converts `item` to a dict.

    Args:
        item (Any): item to convert to a dict.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        dict[Hashable, Any]: derived from `item`.

    """
    return dict(dictify(item))


@functools.singledispatch
def to_list(item: Any, /) -> list[Any]:
    """Converts `item` to a list.

    Args:
        item (Any): item to convert to a list.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        list[Any]: derived from `item`.

    """
    if isinstance(item, list):
        return item
    if _is_collection(item):
        return list(item)
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


@to_list.register(str)
def str_to_list(item: str, /) -> list[Any]:
    """Converts a str representation of a list to a list.

    Args:
        item (str): str with a python list literal (for example, "[1, 2, 3]").

    Raises:
        ValueError: if `item` is not a valid python literal.
        TypeError: if `item` is a literal that is not a list.

    Returns:
        list[Any]: derived from `item`.

    """
    try:
        result = ast.literal_eval(item)
    except SyntaxError as error:
        raise ValueError(f"{item!r} is not a valid python literal") from error
    if not isinstance(result, list):
        raise TypeError(f"{item!r} is not a list literal")
    return result


@functools.singledispatch
def to_float(item: Any, /) -> float:
    """Converts `item` to a float.

    Args:
        item (Any): item to convert to a float.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        float: derived from `item`.

    """
    if isinstance(item, float):
        return item
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


@to_float.register(int)
def int_to_float(item: int, /) -> float:
    """Converts an int to a float.

    Args:
        item (int): item to convert to a float.

    Returns:
        float: derived from `item`.

    """
    return float(item)


@to_float.register(str)
def str_to_float(item: str, /) -> float:
    """Converts a str to a float.

    Args:
        item (str): item to convert to a float.

    Raises:
        ValueError: if `item` is not a valid representation of a float.

    Returns:
        float: derived from `item`.

    """
    return float(item)


@functools.singledispatch
def to_path(item: Any, /) -> pathlib.Path:
    """Converts `item` to a pathlib.Path.

    Args:
        item (Any): item to convert to a pathlib.Path.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        pathlib.Path: derived from `item`.

    """
    if isinstance(item, pathlib.Path):
        return item
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


@to_path.register(str)
@pathlibify.register(str)
def str_to_path(item: str, /) -> pathlib.Path:
    """Converts a str to a pathlib.Path.

    Args:
        item (str): item to convert to a pathlib.Path.

    Returns:
        pathlib.Path: derived from `item`.

    """
    return pathlib.Path(item)


@functools.singledispatch
def to_str(item: Any, /) -> str:
    """Converts `item` to a str.

    Args:
        item (Any): item to convert to a str.

    Raises:
        TypeError: if `item` is a type that is not registered.

    Returns:
        str: derived from `item`.

    """
    if isinstance(item, str):
        return item
    raise TypeError(_UNSUPPORTED.format(name=type(item).__name__))


@to_str.register(int)
def int_to_str(item: int, /) -> str:
    """Converts an int to a str.

    Args:
        item (int): item to convert to a str.

    Returns:
        str: derived from `item`.

    """
    return str(item)


@to_str.register(float)
def float_to_str(item: float, /) -> str:
    """Converts a float to a str.

    Args:
        item (float): item to convert to a str.

    Returns:
        str: derived from `item`.

    """
    return str(item)


@to_str.register(list)
def list_to_str(item: list[Any], /) -> str:
    """Converts a list to a str.

    Args:
        item (list[Any]): item to convert to a str.

    Returns:
        str: the items in `item` separated by a comma and a space.

    """
    return ", ".join(str(i) for i in item)


@to_str.register(type(None))
def none_to_str(item: None, /) -> str:
    """Converts None to a str.

    Args:
        item (None): None.

    Returns:
        str: "None".

    """
    return "None"


@to_str.register(pathlib.PurePath)
def path_to_str(item: pathlib.PurePath, /) -> str:
    """Converts a pathlib.Path to a str.

    Args:
        item (pathlib.PurePath): item to convert to a str.

    Returns:
        str: derived from `item`.

    """
    return str(item)


@to_str.register(datetime.datetime)
def datetime_to_str(
    item: datetime.datetime,
    /,
    time_format: str | None = "%Y-%m-%d_%H-%M",
) -> str:
    """Returns datetime `item` as a str based on `time_format`.

    Args:
        item (datetime.datetime): datetime object to convert to a str.
        time_format (str | None): format to create a str from datetime. The
            passed argument should follow the rules of datetime.strftime.
            Defaults to "%Y-%m-%d_%H-%M".

    Returns:
        str: converted datetime `item`.

    """
    return item.strftime(time_format or "%Y-%m-%d_%H-%M")


datetime_to_string = datetime_to_str
