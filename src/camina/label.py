"""System and functions for inferring object and class names.

Contents:
    namify: returns a str name for an item.
    Name (base.Descriptor): descriptor that supplies an inferred name attribute
        to an object.
    get_key_namer: returns the global function used to infer names for items.
    get_method_namer: returns the global function used to name factory methods.

To Do:
    Add support for names inferred from more types.

"""

from __future__ import annotations

import dataclasses
import inspect
from collections.abc import Callable
from typing import Any

from . import base, configuration, modify


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


def get_key_namer() -> Callable[[Any], str | None]:
    """Returns the global function used to name items.

    Returns:
        Callable[[Any], str | None]: the function set by
            `camina.set_key_namer` or, by default, `camina.namify`.

    """
    return configuration._KEY_NAMER or namify


def get_method_namer() -> Callable[[Any], str | None]:
    """Returns the global function used to name factory methods.

    Returns:
        Callable[[Any], str | None]: the function set by
            `camina.set_method_namer` or, by default, a function that prepends
            "from_" to the result of `camina.namify`.

    """
    return configuration._METHOD_NAMER or (lambda x: f"from_{namify(x)}")


@dataclasses.dataclass(eq=False)
class Name(base.Descriptor):
    """Descriptor for a name attribute.

    This class automatically provides a name attribute to an object. If a name
    has not been stored, the name is created by calling `namer` with the class
    of the object that owns the descriptor. If `namer` is None, the global key
    namer (`camina.namify` unless changed by `camina.set_key_namer`) is used.

    Attributes:
        namer (Callable[[Any], str | None] | None): function that creates a name
            if one has not been stored. It is passed the class of the object
            that owns this descriptor. Defaults to None.

    """

    namer: Callable[[Any], str | None] | None = None

    # Dunder Methods

    def __get__(self, instance: object, owner: type[Any] | None = None) -> Any:
        """Returns stored name or one created by `namer`.

        Args:
            instance (object): object of which this descriptor is an attribute.
                It is None when the descriptor is accessed through its class.
            owner (type[Any] | None): class of `instance`. Defaults to None.

        Returns:
            Any: stored name, a name created by `namer`, or (if accessed through
                the class) this descriptor.

        """
        if instance is None:
            return self
        try:
            return getattr(instance, self.private_name)
        except AttributeError:
            namer = self.namer or get_key_namer()
            return namer(type(instance))

    def __set__(self, instance: object, value: Any) -> None:
        """Stores `value` in `private_name` of `instance`.

        If `value` is a Name instance (which happens when a Name is the default
        value of a dataclass field), nothing is stored so that a name is
        inferred when it is sought.

        Args:
            instance (object): object of which this descriptor is an attribute.
            value (Any): name to store.

        """
        if isinstance(value, Name):
            return
        setattr(instance, self.private_name, value)
