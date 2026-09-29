"""Base classes for extensible, flexible, lightweight containers.

Contents:
    Bunch (Collection, abc.ABC): base class for general containers in `camina`.
        It requires subclasses to have `add`, `delete`, and `subset` methods.
    Descriptor (object): interface for descriptors. `__get__`, `__set__`, and a
        fully-featured `__set_name__` are provided. `__set_name__` creates
        `attribute_name`, `owner`, and `private_name` attributes.
    Proxy (Container): basic wrapper for a stored python object. Dunder methods
        attempt to intelligently apply access methods to either the wrapper or
        the wrapped item.
    resolve_default: returns a default value, calling it if it is callable.

To Do:
    Add more dunder methods to address less common and fringe cases for use
        of a Proxy class.

"""

from __future__ import annotations

import abc
import copy
import dataclasses
from collections.abc import Collection, Container, Hashable, Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Self


def resolve_default(default: Any) -> Any:
    """Returns `default`, calling it first if it is callable.

    This supports the `default_factory` attributes in `camina` containers, which
    can either store a default value or a callable that creates one.

    Args:
        default (Any): a default value or a callable that returns a default
            value.

    Returns:
        Any: the result of calling `default` if it is callable. Otherwise,
            `default` is returned as is.

    """
    return default() if callable(default) else default


@dataclasses.dataclass
class Bunch(Collection[Any], abc.ABC):
    """Base for general `camina` collections.

    A Bunch differs from a general python Collection in 4 ways:
        1) It must include an `add` method which provides the default mechanism
            for adding new items to the collection. `add` allows a subclass to
            designate the preferred method of adding to the collections`s stored
            data without replacing other access methods.
        2) It must include a `delete` method which provides the default
            mechanism for deleting items in the collection. `delete` is called
            by the `__delitem__` dunder method to delete stored items.
        3) A subclass must include a `subset` method with optional `include` and
            `exclude` parameters for returning a subset of the Bunch subclass.
        4) It supports the '+' operator being used to join a Bunch subclass
            instance of the same python type (mapping, sequence, tuple, etc.).
            The '+' operator calls the Bunch subclass `add` method to implement
            how the added item(s) is/are added to a copy of the Bunch subclass
            instance. The '+=' operator calls `add` on the instance itself.

    Attributes:
        contents (Collection[Any]): stored collection of items.

    """

    contents: Collection[Any]

    # Required Subclass Methods

    @abc.abstractmethod
    def add(self, item: Any, *args: Any, **kwargs: Any) -> None:
        """Adds `item` to `contents`.

        Args:
            item (Any): item to add to `contents`.
            *args (Any): positional arguments.
            **kwargs (Any): keyword arguments.

        """

    @abc.abstractmethod
    def delete(self, item: Any, *args: Any, **kwargs: Any) -> None:
        """Deletes `item` from `contents`.

        Args:
            item (Any): item or key to delete in `contents`.
            *args (Any): positional arguments.
            **kwargs (Any): keyword arguments.

        Raises:
            KeyError: if `item` is not in `contents`. Subclasses should
                implement this error.

        """

    @abc.abstractmethod
    def subset(
        self,
        include: Collection[Any] | Any | None = None,
        exclude: Collection[Any] | Any | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        """Returns a new instance with a subset of `contents`.

        This method applies `include` before `exclude` if both are passed. If
        `include` is None, all existing items will be added to the new subset
        class instance before `exclude` is applied.

        Args:
            include (Collection[Any] | Any | None): item(s) to include in the
                new Bunch. Defaults to None.
            exclude (Collection[Any] | Any | None): item(s) to exclude from the
                new Bunch. Defaults to None.
            *args (Any): positional arguments.
            **kwargs (Any): keyword arguments.

        Returns:
            Bunch: a new instance of the same type with a subset of `contents`.

        """

    # Dunder Methods

    def __add__(self, other: Any) -> Self:
        """Returns a copy with `other` combined with `contents` by `add`.

        Args:
            other (Any): item to add to the copy's `contents` using the `add`
                method.

        Returns:
            Bunch: a deep copy of this instance with `other` added.

        """
        result = copy.deepcopy(self)
        result.add(item=other)
        return result

    def __iadd__(self, other: Any) -> Self:
        """Combines `other` with `contents` in place using the `add` method.

        Args:
            other (Any): item to add to `contents` using the `add` method.

        Returns:
            Bunch: this instance, after `other` has been added.

        """
        self.add(item=other)
        return self

    def __contains__(self, item: object) -> bool:
        """Returns whether `item` is in `contents`.

        Args:
            item (object): item to look for in `contents`.

        Returns:
            bool: whether `item` is in `contents`.

        """
        return item in self.contents

    def __delitem__(self, item: Hashable) -> None:
        """Deletes `item` from `contents`.

        Args:
            item (Hashable): item or key to delete in `contents`.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        self.delete(item=item)

    def __iter__(self) -> Iterator[Any]:
        """Returns iterator of `contents`.

        Returns:
            Iterator: of `contents`.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of `contents`.

        Returns:
            int: length of `contents`.

        """
        return len(self.contents)


class Descriptor:
    """Base for descriptors.

    Since Python currently lacks an abstract base class for descriptors, this
    class sets the basic interface for one and offers a fully-featured
    `__set_name__` method. Since `__delete__` isn`t a strict requirement for
    a descriptor (typical use cases simply rely on a call to `__get__`), it is
    not included.

    The code in this class is derived from a HowTo Guide in the official Python
    docs: https://docs.python.org/3/howto/descriptor.html

    Attributes:
        attribute_name (str): name of the attribute for the Descriptor instance
            in `owner`. It is set by `__set_name__`.
        private_name (str): `attribute_name` with a leading underscore added.
            This attribute contains the name of an attribute in the instance of
            `owner` (and not the descriptor) where the data for a descriptor
            will be stored. It is set by `__set_name__`.
        owner (type[Any]): class of which the Descriptor instance is an
            attribute. It is set by `__set_name__`.

    """

    attribute_name: str
    private_name: str
    owner: type[Any]

    # Dunder Methods

    def __get__(self, instance: object, owner: type[Any] | None = None) -> Any:
        """Returns item stored in `private_name` of `instance`.

        Args:
            instance (object): object of which this descriptor is an attribute.
                It is None when the descriptor is accessed through its class.
            owner (type[Any] | None): class of `instance`. Defaults to None.

        Returns:
            Any: stored item or, if accessed through the class, this descriptor.

        """
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance: object, value: Any) -> None:
        """Stores `value` in `private_name` of `instance`.

        Args:
            instance (object): object of which this descriptor is an attribute.
            value (Any): item to store.

        """
        setattr(instance, self.private_name, value)

    def __set_name__(self, owner: type[Any], name: str) -> None:
        """Creates attributes based on `owner` and `name`.

        Args:
            owner (type[Any]): class of which this descriptor is an attribute.
            name (str): name of this attribute in `owner`.

        """
        self.attribute_name = name
        self.private_name = f"_{name}"
        self.owner = owner


def _is_dunder(name: str) -> bool:
    """Returns whether `name` starts and ends with a double underscore."""
    return name.startswith("__") and name.endswith("__")


@dataclasses.dataclass
class Proxy(Container[Any]):
    """Mostly transparent wrapper class.

    A Proxy differs than an ordinary container in 2 significant ways:
        1) Access methods for getting, setting, and deleting that try to
            intelligently direct the user's call to the proxy or stored object.
            So, for example, when a user tries to set an attribute on the proxy,
            the method will replace an attribute that exists in the proxy if
            one exists. But if there is no such attribute, the set method is
            applied to the object stored in `contents`. If `contents` refuses
            the new attribute (as built-in types do), it is set on the proxy.
        2) When an `in` call is made, the `__contains__` method first looks to
            see if the item is stored in `contents` (if `contents` is a
            collection). If that check gets an error, the method then checks
            if the item is equivalent to `contents`. This allows a Proxy to be
            agnostic as to the type of item(s) in `contents` while returning the
            expected result from an `in` call.

    Special (dunder) attributes are never looked up on `contents` by
    `__getattr__` because Python finds special methods on types, not instances.
    The common container and call protocols (`__getitem__`, `__setitem__`,
    `__delitem__`, `__iter__`, `__len__`, and `__call__`) are explicitly
    forwarded to `contents`.

    Attributes:
        contents (Any): any stored item(s). Defaults to None.

    To Do:
        Add more dunder methods to address less common and fringe cases for use
            of a Proxy class.

    """

    contents: Any = None

    # Dunder Methods

    def __contains__(self, item: object) -> bool:
        """Returns whether `item` is in or the equivalent to `contents`.

        Args:
            item (object): item to check versus `contents`.

        Returns:
            bool: if `item` is in or equivalent to `contents` (True). Otherwise,
                it returns False.

        """
        try:
            return item in self.contents
        except TypeError:
            return item is self.contents or bool(item == self.contents)

    def __getattr__(self, attribute: str) -> Any:
        """Looks for `attribute` in `contents`.

        If `attribute` exists in the Proxy subclass, this method will not be
        called and the contents of that attribute will be returned.

        Args:
            attribute (str): name of attribute to return.

        Raises:
            AttributeError: if `attribute` is not found in `contents`.

        Returns:
            Any: matching attribute from `contents`.

        """
        if attribute == "contents" or _is_dunder(attribute):
            raise AttributeError(
                f"{type(self).__name__} has no attribute {attribute!r}"
            )
        return getattr(self.contents, attribute)

    def __setattr__(self, attribute: str, value: Any) -> None:
        """Sets `attribute` to `value`.

        If `attribute` exists in this class instance, its new value is set to
        `value`. Otherwise, `attribute` and `value` are set in what is stored in
        `contents` (whether or not the attribute previously existed there). If
        `contents` is None or does not accept new attributes, `attribute` is set
        on this class instance.

        Args:
            attribute (str): name of attribute to set.
            value (Any): value to store in the attribute `attribute`.

        """
        if (
            attribute == "contents"
            or attribute in self.__dict__
            or hasattr(type(self), attribute)
            or self.contents is None
        ):
            object.__setattr__(self, attribute, value)
        else:
            try:
                setattr(self.contents, attribute, value)
            except (AttributeError, TypeError):
                object.__setattr__(self, attribute, value)

    def __delattr__(self, attribute: str) -> None:
        """Deletes `attribute`.

        If `attribute` exists in this class instance, it is deleted. Otherwise,
        this method attempts to delete `attribute` from what is stored in
        `contents`.

        Args:
            attribute (str): name of attribute to delete.

        Raises:
            AttributeError: if `attribute` is neither found in the Proxy
                subclass nor in `contents`.

        """
        if attribute in self.__dict__:
            object.__delattr__(self, attribute)
        else:
            try:
                delattr(self.contents, attribute)
            except (AttributeError, TypeError) as error:
                raise AttributeError(
                    f"{attribute!r} was not found in {type(self).__name__} or "
                    f"its contents"
                ) from error

    def __bool__(self) -> bool:
        """Returns True because a Proxy instance is always truthy.

        Without this method, defining `__len__` would make the truth value of a
        Proxy depend on (and possibly fail because of) the type of `contents`.

        Returns:
            bool: True.

        """
        return True

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Calls `contents` with the passed arguments.

        Args:
            *args (Any): positional arguments to pass to `contents`.
            **kwargs (Any): keyword arguments to pass to `contents`.

        Returns:
            Any: the result of calling `contents`.

        """
        return self.contents(*args, **kwargs)

    def __delitem__(self, key: Any) -> None:
        """Deletes `key` from `contents`.

        Args:
            key (Any): key or index in `contents` to delete.

        """
        del self.contents[key]

    def __getitem__(self, key: Any) -> Any:
        """Returns the item at `key` in `contents`.

        Args:
            key (Any): key or index in `contents`.

        Returns:
            Any: item stored in `contents` at `key`.

        """
        return self.contents[key]

    def __iter__(self) -> Iterator[Any]:
        """Returns an iterator of `contents`.

        Returns:
            Iterator: of `contents`.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns the length of `contents`.

        Returns:
            int: length of `contents`.

        """
        return len(self.contents)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        Args:
            key (Any): key or index in `contents`.
            value (Any): item to store in `contents` at `key`.

        """
        self.contents[key] = value
