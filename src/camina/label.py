"""System and functions for inferring object and class names.

Contents:
    namify: returns a str name for an item.

To Do:
    Add support for names inferred from more types.

"""

from __future__ import annotations

import inspect
from typing import Any

from . import modify


def namify(item: Any, /, default: str | None = None) -> str | None:
    """Returns str name representation of `item`.

    The name is determined as follows:
        1) A str `item` is its own name.
        2) An instance with a `name` attribute that is a str uses that value.
        3) An item with a `__name__` attribute (for example, a class or function)
            uses that value converted to snake case.
        4) Otherwise, the snake case name of the class of `item` is used.

    Args:
        item (Any): item to determine a str name.
        default (str | None): default name to return if other methods at name
            creation fail to produce a name. Defaults to None.

    Returns:
        str | None: a name representation of `item`, or `default` if no name
            could be created.

    """
    if isinstance(item, str):
        return item
    if not inspect.isclass(item):
        name = getattr(item, "name", None)
        if isinstance(name, str):
            return name
    name = getattr(item, "__name__", None)
    if not isinstance(name, str):
        name = type(item).__name__
    return modify.snakify(name) if name else default
