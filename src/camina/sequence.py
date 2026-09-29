"""List-like classes.

Contents:
    Listing (base.Bunch, MutableSequence): drop-in replacement for a python
        list with additional functionality.
    Hybrid (Listing): iterable with both dict and list interfaces. Stored items
        must be hashable or have a `name` attribute.

To Do:
    Add support for names that are not str types in Hybrid.

"""

from __future__ import annotations

import dataclasses
from collections.abc import (
    Collection,
    Hashable,
    Mapping,
    MutableSequence,
    Sequence,
)
from typing import TYPE_CHECKING, Any

from . import base, configuration, convert, label

if TYPE_CHECKING:
    from typing import Self


def _is_sequence(item: Any) -> bool:
    """Returns whether `item` is a sequence other than a str or bytes type.

    Args:
        item (Any): item to check.

    Returns:
        bool: whether `item` is a non-str sequence.

    """
    return isinstance(item, Sequence) and not isinstance(
        item, (str, bytes, bytearray)
    )


@dataclasses.dataclass
class Listing(base.Bunch, MutableSequence[Any]):
    """Basic camina list replacement.

    A Listing differs from an ordinary python list in ways required by
    inheriting from Bunch: `add`, `delete`, and `subset` methods, and allowing
    the '+' operator to join Listings with other list-like objects) and in 1
    other way:
        1) It includes a `prepend` method for adding one or more items to the
            beginning of the stored list.

    The `add` method attempts to extend `contents` with the item to be added.
    If `item` is not a sequence (or is a str), it appends the item to
    `contents`.

    Attributes:
        contents (MutableSequence[Any]): items to store in a list. Defaults to
            an empty list.

    """

    contents: MutableSequence[Any] = dataclasses.field(default_factory=list)

    # Instance Methods

    def add(self, item: Any | Sequence[Any]) -> None:
        """Tries to extend `contents` with `item`. Otherwise, it appends.

        The method will extend all passed sequences, except str types, which it
        will append.

        Args:
            item (Any | Sequence[Any]): item(s) to add to `contents`.

        """
        if _is_sequence(item):
            for thing in item:
                self.append(thing)
        else:
            self.append(item)

    def delete(self, item: int | slice) -> None:
        """Deletes item at the index in `contents`.

        Args:
            item (int | slice): index (or slice) in `contents` to delete.

        Raises:
            IndexError: if the index `item` is out of range.

        """
        del self.contents[item]

    def insert(self, index: int, item: Any) -> None:
        """Inserts `item` at `index` in `contents`.

        Args:
            index (int): index to insert `item` at.
            item (Any): object to be inserted.

        """
        self.contents.insert(index, item)

    def prepend(self, item: Any | Sequence[Any]) -> None:
        """Prepends `item` to `contents`.

        If `item` is a non-str sequence, `prepend` adds its contents to the
        stored list in the order they appear in `item`.

        Args:
            item (Any | Sequence[Any]): item(s) to prepend to `contents`.

        """
        if _is_sequence(item):
            for thing in reversed(item):
                self.insert(0, thing)
        else:
            self.insert(0, item)

    def subset(
        self,
        include: Any | Sequence[Any] | None = None,
        exclude: Any | Sequence[Any] | None = None,
    ) -> Self:
        """Returns a new instance with a subset of `contents`.

        This method applies `include` before `exclude` if both are passed. If
        `include` is None, all existing items will be added to the new subset
        class instance before `exclude` is applied.

        Args:
            include (Any | Sequence[Any] | None): item(s) to include in the new
                instance. Defaults to None.
            exclude (Any | Sequence[Any] | None): item(s) to exclude in the new
                instance. Defaults to None.

        Raises:
            ValueError: if `include` and `exclude` are both None.

        Returns:
            Listing: with only items from `include` and no items in `exclude`.

        """
        if include is None and exclude is None:
            raise ValueError("include or exclude must not be None")
        contents = list(self.contents)
        if include is not None:
            included = list(convert.iterify(include))
            contents = [i for i in contents if self._is_in(i, included)]
        if exclude is not None:
            excluded = list(convert.iterify(exclude))
            contents = [i for i in contents if not self._is_in(i, excluded)]
        return dataclasses.replace(self, contents=contents)

    # Private Methods

    def _is_in(self, item: Any, collection: Collection[Any]) -> bool:
        """Returns whether `item` is in `collection`.

        Subclasses can override this method to change how items are matched by
        `subset`.

        Args:
            item (Any): item to look for.
            collection (Collection[Any]): items to search.

        Returns:
            bool: whether `item` is in `collection`.

        """
        return item in collection

    # Dunder Methods

    def __getitem__(self, index: Any) -> Any:
        """Returns value(s) for `index` in `contents`.

        Args:
            index (Any): index (or slice) to search for in `contents`.

        Returns:
            Any: item stored in `contents` at `index`. If `index` is a slice,
                a new instance with the sliced items is returned.

        """
        if isinstance(index, slice):
            return dataclasses.replace(self, contents=self.contents[index])
        return self.contents[index]

    def __setitem__(self, index: Any, value: Any) -> None:
        """Sets `index` in `contents` to `value`.

        Args:
            index (Any): index (or slice) to set `value` to in `contents`.
            value (Any): value to be set at `index` in `contents`.

        """
        self.contents[index] = value


@dataclasses.dataclass
class Hybrid(Listing):
    """Iterable that has both a dict and list interfaces.

    Hybrid combines the functionality and interfaces of python dicts and lists.
    It allows duplicate keys and list-like iteration while supporting the easier
    access methods of dictionaries. In order to support this hybrid approach to
    iterables, Hybrid can only store items that are hashable or have a `name`
    attribute or property that contains or returns a hashable value.

    A Hybrid inherits the differences between a Listing and an ordinary python
    list.

    A Hybrid differs from a Listing in 4 significant ways:
        1) It only stores hashable items or objects for which a str name can be
            derived (using the namify function).
        2) Hybrid has an interface of both a dict and a list, but stores a list.
            Hybrid does this by taking advantage of the `name` attribute or
            hashability of stored items. A `name` or hash acts as a key to
            create the facade of a dict with the items in the stored list
            serving as values. This allows for duplicate keys for storing items,
            simpler iteration than a dict, and support for returning multiple
            matching items. This design comes at the expense of lookup speed. As
            a result, Hybrid should only be used if a high volume of access
            calls is not anticipated. Ordinarily, the loss of lookup speed
            should have negligible effect on overall performance.
        3) Hybrids should not store int types. This ensures that when, for
            example, a `hybrid[3]` is called, the item at that index is
            returned. If int types are stored, that call would create
            uncertainty as to whether an index or item should be returned. By
            design, int types are assumed to be calls to return the item at that
            index.
        4) When using dict access methods, a Hybrid of matches may be returned
            because a Hybrid allows duplicate pseudo-keys to be used.

    Attributes:
        contents (MutableSequence[Hashable]): items to store that are hashable
            or have a `name` attribute. Defaults to an empty list.
        default_factory (Any | None): default value to return or default
            function to call when the `get` method is used. Defaults to None.

    """

    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory=list
    )
    default_factory: Any | None = None

    # Initialization Methods

    def __post_init__(self) -> None:
        """Validates the items in `contents`.

        Raises:
            TypeError: if any item in `contents` is neither hashable nor has a
                `name` attribute that is a str.

        """
        for item in self.contents:
            self._validate(item)

    # Instance Methods

    def delete(self, item: Any | int | slice) -> None:
        """Deletes item in `contents`.

        If `item` is not an int (or slice), this method looks for a matching
        `name` attribute in the stored instances and deletes all such items. If
        `item` is an int, only the item at that index is deleted.

        Args:
            item (Any | int | slice): name or index in `contents` to delete.

        Raises:
            KeyError: if `item` is a name that does not match any stored item.

        """
        if isinstance(item, (int, slice)):
            del self.contents[item]
            return
        indices = [i for i, _ in self._matches(item)]
        if not indices:
            raise KeyError(f"{item} is not in {self.__class__.__name__}")
        for index in reversed(indices):
            del self.contents[index]

    def get(self, key: Hashable, default: Any | None = None) -> Any:
        """Returns value in `contents` or default options.

        Args:
            key (Hashable): key (or index) for value in `contents`.
            default (Any | None): default value to return if `key` is not found
                in `contents`. Defaults to None, which means that the
                `default_factory` attribute is used.

        Raises:
            KeyError: if `key` is not in the Hybrid and `default` and the
                `default_factory` attribute are both None.

        Returns:
            Any: value matching key in `contents` or `default_factory` value.

        """
        try:
            return self[key]
        except (KeyError, IndexError, TypeError):
            if default is not None:
                return default
            if self.default_factory is None:
                raise KeyError(f"{key} is not in the Hybrid") from None
            return base.resolve_default(self.default_factory)

    def items(self) -> tuple[tuple[Hashable, Any], ...]:
        """Emulates python dict `items` method.

        Returns:
            tuple[tuple[Hashable, Any], ...]: a tuple equivalent to
                dict.items(). A Hybrid cannot actually create an ItemsView
                because that would eliminate any duplicate keys, which are
                permitted by Hybrid.

        """
        return tuple(zip(self.keys(), self.values(), strict=True))

    def keys(self) -> tuple[Hashable, ...]:
        """Emulates python dict `keys` method.

        Returns:
            tuple[Hashable, ...]: a tuple equivalent to dict.keys(). A Hybrid
                cannot actually create an KeysView because that would eliminate
                any duplicate keys, which are permitted by Hybrid.

        """
        namer = label.get_key_namer()
        return tuple(namer(c) for c in self.contents)

    def insert(self, index: int, item: Any) -> None:
        """Inserts `item` at `index` in `contents`.

        Args:
            index (int): index to insert `item` at.
            item (Any): object to be inserted.

        Raises:
            TypeError: if `item` is neither hashable nor has a `name` attribute
                that is a str.

        """
        self._validate(item)
        super().insert(index, item)

    def setdefault(
        self,
        key: Any = configuration._MISSING,
        default: Any | None = None,
        *,
        value: Any = configuration._MISSING,
    ) -> Any:
        """Sets the default value for `get` or acts like `dict.setdefault`.

        If the keyword argument `value` is passed, it is stored as the default
        value (or callable that creates one) that `get` returns when a key is
        not found. Otherwise, `key` is looked up. If it is not found, `default`
        is appended to `contents`.

        Args:
            key (Any): name for which to add `default` if it is not in
                `contents`.
            default (Any | None): item to add if `key` is not in `contents`.
                Defaults to None.
            value (Any): default value to return when `get` is called and the
                `default` parameter to `get` is None.

        Raises:
            TypeError: if neither `key` nor `value` is passed.

        Returns:
            Any: None if `value` is passed. Otherwise, the item(s) matching
                `key` or `default` if there is no match.

        """
        if value is not configuration._MISSING:
            self.default_factory = value
            return None
        if key is configuration._MISSING:
            raise TypeError("setdefault requires either a key or a value")
        try:
            return self[key]
        except KeyError:
            self.append(default)
            return default

    def update(self, items: Mapping[Any, Any]) -> None:
        """Mimics the dict `update` method by extending `contents` with `items`.

        Args:
            items (Mapping[Any, Any]): items to add to the `contents` attribute.
                The values of `items` are added to `contents` and the keys
                become the `name` attributes of those values. As a result, the
                keys of `items` are discarded. To mimic dict `update`, the
                passed `items` values are added to `contents` by the `extend`
                method which adds the values to the end of `contents`.

        """
        self.extend(list(items.values()))

    def values(self) -> tuple[Any, ...]:
        """Emulates python dict `values` method.

        Returns:
            tuple[Any, ...]: a tuple equivalent to dict.values(). A Hybrid
                cannot actually create an ValuesView because that would
                eliminate any duplicate keys, which are permitted by Hybrid.

        """
        return tuple(self.contents)

    # Private Methods

    def _is_in(self, item: Any, collection: Collection[Any]) -> bool:
        """Returns whether `item` or its name is in `collection`.

        Args:
            item (Any): item to look for.
            collection (Collection[Any]): items and names to search.

        Returns:
            bool: whether `item` or the name of `item` is in `collection`.

        """
        return item in collection or label.get_key_namer()(item) in collection

    def _matches(self, key: Hashable) -> list[tuple[int, Any]]:
        """Returns the indices and items with a name equal to `key`.

        Args:
            key (Hashable): name to look for.

        Returns:
            list[tuple[int, Any]]: indices and matching items in `contents`.

        """
        namer = label.get_key_namer()
        return [(i, c) for i, c in enumerate(self.contents) if namer(c) == key]

    @staticmethod
    def _validate(item: Any) -> None:
        """Checks that `item` can be stored in a Hybrid.

        Args:
            item (Any): item to validate.

        Raises:
            TypeError: if `item` is neither hashable nor has a `name` attribute
                that is a str.

        """
        try:
            hash(item)
        except TypeError:
            if not isinstance(getattr(item, "name", None), str):
                raise TypeError(
                    "items stored in a Hybrid must be hashable or have a "
                    "name attribute"
                ) from None

    # Dunder Methods

    def __contains__(self, item: object) -> bool:
        """Returns whether `item` or a name equal to `item` is in `contents`.

        Args:
            item (object): item or name to look for.

        Returns:
            bool: whether `item` is stored or is the name of a stored item.

        """
        return item in self.contents or bool(self._matches(item))

    def __getitem__(self, key: Hashable | int | slice) -> Any:
        """Returns value(s) for `key` in `contents`.

        If `key` is not an int type, this method looks for a matching `name`
        attribute in the stored instances.

        If `key` is an int type, this method returns the stored item at the
        corresponding index. If `key` is a slice, a Hybrid with the sliced items
        is returned.

        If only one match is found, a single item is returned. If more are
        found, a Hybrid or Hybrid subclass with the matching `name` attributes
        is returned.

        Args:
            key (Hashable | int | slice): name of an item or index to search for
                in `contents`.

        Raises:
            KeyError: if `key` is not an int, slice, or the name of an item.

        Returns:
            Any: value(s) stored in `contents` that correspond to `key`. If
                there is more than one match, the return is a Hybrid or Hybrid
                subclass with that matching stored items.

        """
        if isinstance(key, slice):
            return dataclasses.replace(self, contents=self.contents[key])
        if isinstance(key, int):
            return self.contents[key]
        matches = [c for _, c in self._matches(key)]
        if not matches:
            raise KeyError(f"{key} is not in {self.__class__.__name__}")
        if len(matches) == 1:
            return matches[0]
        return dataclasses.replace(self, contents=matches)

    def __setitem__(self, key: Any | int | slice, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        Args:
            key (Any | int | slice): if key isn't an int (or slice), it is
                ignored (since the `name` attribute of the value will be acting
                as the key). In such a case, the `value` is added to the end of
                `contents`. If key is an int, `value` is assigned at the that
                index number in `contents`.
            value (Any): value to be paired with `key` in `contents`.

        Raises:
            TypeError: if `value` is neither hashable nor has a `name`
                attribute that is a str.

        """
        if isinstance(key, slice):
            values = list(value)
            for item in values:
                self._validate(item)
            self.contents[key] = values
        elif isinstance(key, int):
            self._validate(value)
            self.contents[key] = value
        else:
            self.add(value)
