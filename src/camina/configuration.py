"""Settings for `camina`

Contents:


To Do:


"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any

from . import convert

_ALL_KEYS: list[Any] = ['all', 'All', ['all'], ['All']]
_DEFAULT_KEYS: list[Any] = [
    'default', 'defaults', 'Default', 'Defaults', ['default'], ['defaults'],
    ['Default'], ['Defaults']]
_KEY_NAMER: Callable[[object | type[Any]], str] = convert.namify
_METHOD_NAMER: Callable[[object | type[Any]], str] = (
    lambda x: f'from_{convert.namify(x)}')
_NONE_KEYS: list[Any] = ['none', 'None', ['none'], ['None']]


@dataclasses.dataclass
class _MISSING_VALUE(object):  # noqa: N801
    """Sentinel object for a missing data or parameter.

    This follows the same pattern as the `_MISSING_TYPE` class in the builtin
    dataclasses library.
    https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py#L182-L186

    Because None is sometimes a valid argument or data option, this class
    provides an alternative that does not create the confusion that a default of
    None can sometimes lead to.

    """

    pass  # noqa: PIE790


# _MISSING, instance of MISSING_VALUE, should be used for missing values as an
# alternative to None. This provides a fuller repr and traceback.
_MISSING = _MISSING_VALUE()


def set_key_namer(namer: Callable[[object | type[Any]], str]) -> None:
    """Sets the global default function used to name items.

    Args:
        namer (Callable[[object | Type[Any]], str]): function that returns a
            str name of any item passed.

    Raises:
        TypeError: if 'namer' is not callable.

    """
    if isinstance(namer, Callable):
        globals()['KEYER'] = namer
    else:
        raise TypeError('namer argument must be a callable')

def set_method_namer(namer: Callable[[object | type[Any]], str]) -> None:
    """Sets the global default function used to name factory methods.

    Args:
        namer (Callable[[object | Type[Any]], str]): function that returns a
            str name of any item passed.

    Raises:
        TypeError: if 'namer' is not callable.

    """
    if isinstance(namer, Callable):
        globals()['_METHOD_NAMER'] = namer
    else:
        raise TypeError('namer argument must be a callable')
