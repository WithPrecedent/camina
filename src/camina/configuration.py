"""Global settings and sentinels for `camina`.

Contents:
    set_key_namer: sets the global function used to infer names (keys) for
        items.
    set_method_namer: sets the global function used to name factory methods.

The module-level constants (`_ALL_KEYS`, `_DEFAULT_KEYS`, and `_NONE_KEYS`)
hold the wildcard keys recognized by `camina.Catalog`. `_MISSING` is a sentinel
for missing data or parameters when `None` is a valid value.

To Do:
    Add a mechanism for users to customize the wildcard keys.

"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any

_ALL_KEYS: list[Any] = ["all", "All", ["all"], ["All"]]
_DEFAULT_KEYS: list[Any] = [
    "default",
    "defaults",
    "Default",
    "Defaults",
    ["default"],
    ["defaults"],
    ["Default"],
    ["Defaults"],
]
_NONE_KEYS: list[Any] = ["none", "None", ["none"], ["None"]]

# `None` means that the default namers in `camina.label` are used.
_KEY_NAMER: Callable[[Any], str | None] | None = None
_METHOD_NAMER: Callable[[Any], str | None] | None = None


@dataclasses.dataclass
class _MISSING_VALUE:  # noqa: N801
    """Sentinel object for a missing data or parameter.

    This follows the same pattern as the `_MISSING_TYPE` class in the builtin
    dataclasses library.
    https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py#L182-L186

    Because None is sometimes a valid argument or data option, this class
    provides an alternative that does not create the confusion that a default of
    None can sometimes lead to.

    """


# `_MISSING`, the only instance of `_MISSING_VALUE`, should be used for missing
# values as an alternative to None. This provides a fuller repr and traceback.
_MISSING = _MISSING_VALUE()


def set_key_namer(namer: Callable[[Any], str | None] | None) -> None:
    """Sets the global default function used to name items.

    Args:
        namer (Callable[[Any], str | None] | None): function that returns a str
            name of any item passed. If `None`, the default function
            (`camina.namify`) is restored.

    Raises:
        TypeError: if `namer` is neither callable nor `None`.

    """
    global _KEY_NAMER  # noqa: PLW0603
    if namer is None or callable(namer):
        _KEY_NAMER = namer
    else:
        raise TypeError("namer argument must be a callable or None")


def set_method_namer(namer: Callable[[Any], str | None] | None) -> None:
    """Sets the global default function used to name factory methods.

    Args:
        namer (Callable[[Any], str | None] | None): function that returns a str
            name of any item passed. If `None`, the default function (which
            prepends "from_" to the result of `camina.namify`) is restored.

    Raises:
        TypeError: if `namer` is neither callable nor `None`.

    """
    global _METHOD_NAMER  # noqa: PLW0603
    if namer is None or callable(namer):
        _METHOD_NAMER = namer
    else:
        raise TypeError("namer argument must be a callable or None")
