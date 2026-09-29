"""Extensible, flexible, lightweight dict-like classes.

Contents:
    Dictionary (base.Bunch, MutableMapping): drop-in replacement for a python
        dict with some added functionality.
    Catalog (Dictionary): wildcard-accepting dict which is primarily intended
        for storing different options and strategies. It also returns lists of
        matches if a list of keys is provided.
    ChainDictionary (Dictionary): combines the additional functionality of
        Dictionary with collections.ChainMap from the Python builtin library.
    Repository (Dictionary): stores items using inferred keys when the `add`
        method is called. This is useful for mappings where the key naming is
        controlled by the mapping instead of based on the passed arguments.
        Support for guaranteed unique key creation (using an integer counter) is
        provided out of the box based on the `overwrite` argument.

To Do:
    Add support for ordered subsets of a Dictionary.

"""

from __future__ import annotations

import dataclasses
import itertools
from collections.abc import (
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import TYPE_CHECKING, Any

from . import base, configuration, convert, label, modify

if TYPE_CHECKING:
    from typing import Self


def _subset_mapping(
    contents: Mapping[Hashable, Any],
    include: Hashable | Sequence[Hashable] | None,
    exclude: Hashable | Sequence[Hashable] | None,
) -> dict[Hashable, Any]:
    """Returns a dict with the `include` keys of `contents` minus `exclude`.

    Args:
        contents (Mapping[Hashable, Any]): mapping from which to take a subset.
        include (Hashable | Sequence[Hashable] | None): key(s) to include. Keys
            that are not in `contents` are ignored. If None, all keys are
            included before `exclude` is applied.
        exclude (Hashable | Sequence[Hashable] | None): key(s) to exclude.

    Raises:
        ValueError: if `include` and `exclude` are both None.

    Returns:
        dict[Hashable, Any]: with only keys from `include` and no keys in
            `exclude`.

    """
    if include is None and exclude is None:
        raise ValueError("include or exclude must not be None")
    if include is None:
        subset = dict(contents)
    else:
        keys = list(convert.iterify(include))
        subset = {k: contents[k] for k in keys if k in contents}
    if exclude is not None:
        excluded = list(convert.iterify(exclude))
        subset = {k: v for k, v in subset.items() if k not in excluded}
    return subset


@dataclasses.dataclass
class Dictionary(base.Bunch, MutableMapping[Hashable, Any]):
    """Basic camina dict replacement.

    A Dictionary differs from an ordinary python dict in ways inherited from
    Bunch by requiring `add` and `subset` methods, storing data in `contents`,
    and allowing the '+' operator to join Dictionary instances with other
    mappings, including Dictionary instances.

    In addition, it differs in 2 other significant ways:
        1) When returning `keys`, `values` and `items`, this class returns them
            as tuples instead of KeysView, ValuesView, and ItemsView.
        2) It includes similar functionality to `defaultdict` in the python
            standard library, but the default is used by the `get` method
            (which raises a KeyError if no default exists) and not by
            `__getitem__`. The default can be set with `setdefault`.

    Attributes:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults to
            an empty dict.
        default_factory (Any | None): default value to return or default
            callable to use to create the default value. Defaults to None.

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory=dict
    )
    default_factory: Any | None = None

    # Class Methods

    @classmethod
    def fromkeys(
        cls, keys: Iterable[Hashable], value: Any = None, **kwargs: Any
    ) -> Self:
        """Emulates the `fromkeys` class method from a python dict.

        Args:
            keys (Iterable[Hashable]): items to be keys in a new Dictionary.
            value (Any): the value to use for all values in a new Dictionary.
                Defaults to None.
            **kwargs (Any): additional arguments to pass to the class
                constructor.

        Returns:
            Dictionary: formed from `keys` and `value`.

        """
        return cls(contents=dict.fromkeys(keys, value), **kwargs)

    # Instance Methods

    def add(self, item: Mapping[Hashable, Any], **kwargs: Any) -> None:
        """Adds `item` to the `contents` attribute.

        Args:
            item (Mapping[Hashable, Any]): items to add to `contents` attribute.
            **kwargs (Any): additional key/value pairs to add to `contents`.

        """
        self.contents.update(item, **kwargs)

    def delete(self, item: Hashable) -> None:
        """Deletes `item` in `contents`.

        Args:
            item (Hashable): key in `contents` to delete the key/value pair.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        del self.contents[item]

    def get(self, key: Hashable, default: Any | None = None) -> Any:
        """Returns value in `contents` or default options.

        Args:
            key (Hashable): key for value in `contents`.
            default (Any | None): default value to return if `key` is not found
                in `contents`. Defaults to None, which means that the
                `default_factory` attribute is used.

        Raises:
            KeyError: if `key` is not in the Dictionary and `default` and the
                `default_factory` attribute are both None.

        Returns:
            Any: value matching key in `contents` or `default_factory` value.

        """
        try:
            return self[key]
        except (KeyError, TypeError):
            if default is not None:
                return default
            if self.default_factory is None:
                raise KeyError(f"{key} is not in the Dictionary") from None
            return base.resolve_default(self.default_factory)

    def items(self) -> tuple[tuple[Hashable, Any], ...]:  # type: ignore[override]
        """Emulates python dict `items` method.

        Returns:
            tuple[tuple[Hashable, Any], ...]: a tuple equivalent to
                dict.items().

        """
        return tuple(zip(self.keys(), self.values(), strict=True))

    def keys(self) -> tuple[Hashable, ...]:  # type: ignore[override]
        """Returns `contents` keys as a tuple.

        Returns:
            tuple[Hashable, ...]: a tuple equivalent to dict.keys().

        """
        return tuple(self.contents.keys())

    def popitem(self) -> tuple[Hashable, Any]:
        """Removes and returns the last key/value pair, like `dict.popitem`.

        Raises:
            KeyError: if the Dictionary is empty.

        Returns:
            tuple[Hashable, Any]: the last key and value in `contents`.

        """
        try:
            key = next(reversed(self.contents))
        except StopIteration:
            raise KeyError("popitem(): Dictionary is empty") from None
        return key, self.contents.pop(key)

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
        not found. Otherwise, this method has the same behavior as the
        `setdefault` method of a python dict.

        Args:
            key (Any): key for which to set `default` if it is not in
                `contents`.
            default (Any | None): value to set for `key` if it is not in
                `contents`. Defaults to None.
            value (Any): default value to return when `get` is called and the
                `default` parameter to `get` is None.

        Raises:
            TypeError: if neither `key` nor `value` is passed.

        Returns:
            Any: None if `value` is passed. Otherwise, the value stored for
                `key` in `contents`.

        """
        if value is not configuration._MISSING:
            self.default_factory = value
            return None
        if key is configuration._MISSING:
            raise TypeError("setdefault requires either a key or a value")
        if key not in self.contents:
            self.contents[key] = default
        return self.contents[key]

    def subset(  # type: ignore[override]
        self,
        include: Hashable | Sequence[Hashable] | None = None,
        exclude: Hashable | Sequence[Hashable] | None = None,
    ) -> Self:
        """Returns a new instance with a subset of `contents`.

        This method applies `include` before `exclude` if both are passed. If
        `include` is None, all existing items will be added to the new subset
        class instance before `exclude` is applied.

        Args:
            include (Hashable | Sequence[Hashable] | None): key(s) to include in
                the new Dictionary instance. Keys that are not in `contents` are
                ignored. Defaults to None.
            exclude (Hashable | Sequence[Hashable] | None): key(s) to exclude
                from the new Dictionary instance. Defaults to None.

        Raises:
            ValueError: if `include` and `exclude` are both None.

        Returns:
            Dictionary: with only keys from `include` and no keys in `exclude`.

        """
        contents = _subset_mapping(self.contents, include, exclude)
        return dataclasses.replace(self, contents=contents)

    def values(self) -> tuple[Any, ...]:  # type: ignore[override]
        """Returns `contents` values as a tuple.

        Returns:
            tuple[Any, ...]: a tuple equivalent to dict.values().

        """
        return tuple(self.contents.values())

    # Dunder Methods

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for `key` in `contents`.

        Args:
            key (Hashable): key in `contents` for which a value is sought.

        Returns:
            Any: value stored in `contents`.

        """
        return self.contents[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        Args:
            key (Hashable): key to set in `contents`.
            value (Any): value to be paired with `key` in `contents`.

        """
        self.contents[key] = value


@dataclasses.dataclass
class Catalog(Dictionary):
    """Wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Dictionary and an ordinary
    python dict.

    A Catalog differs from a Dictionary in 5 significant ways:
        1) It recognizes an `all` key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a `default` key which will return all values matching
            keys listed in the `default` attribute. `default` can also be set
            using the `catalog.default = new_default` assignment. If `default`
            is not passed when the instance is initialized, the initial value
            of `default` is `all`.
        3) It recognizes a `none` key which will return `None` (or an empty list
            if `always_return_list` is True). If `default_factory` is set, the
            default value is returned instead.
        4) It supports a list of keys being accessed with the matching values
            returned. For example, `catalog[["first_key", "second_key"]]` will
            return the values for those keys in a list `["first_value",
            "second_value"]`. Keys that are not found are skipped.
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if `always_return_list` is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single type will be returned.

    Attributes:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults to
            an empty dict.
        default_factory (Any | None): default value to return or default
            callable to use to create the default value. Defaults to None.
        default (Any | None): a list of keys in `contents` which will be used to
            return items when `default` is sought. Defaults to "all".
        always_return_list (bool): whether to return a list even when the key
            passed is not a list or special access key (True) or to return a
            list only when a list or special access key is used (False).
            Defaults to False.

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory=dict
    )
    default_factory: Any | None = None
    default: Any | None = "all"
    always_return_list: bool = False

    # Instance Methods

    def delete(self, item: Hashable | Sequence[Hashable]) -> None:
        """Deletes `item` in `contents`.

        Args:
            item (Hashable | Sequence[Hashable]): name(s) of key(s) in
                `contents` to delete the key/value pair.

        Raises:
            KeyError: if any key in `item` is not in `contents`. No key is
                deleted in that case.

        """
        try:
            if item in self.contents:
                del self.contents[item]
                return
        except TypeError:
            pass
        keys = list(convert.iterify(item))
        if all(k in self.contents for k in keys):
            for key in keys:
                del self.contents[key]
        else:
            raise KeyError(f"{item} not found in the Catalog")

    # Dunder Methods

    def __getitem__(
        self, key: Hashable | Sequence[Hashable]
    ) -> Any | Sequence[Any]:
        """Returns value(s) for `key` in `contents`.

        The method searches for `all`, `default`, and `none` matching wildcard
        options before searching for direct matches in `contents`.

        Args:
            key (Hashable | Sequence[Hashable]): key(s) in `contents`.

        Raises:
            KeyError: if `key` is not a wildcard and is not found in `contents`.

        Returns:
            Any | Sequence[Any]: value(s) stored in `contents`.

        """
        # Returns a list of all values if the `all` key is sought.
        if key in configuration._ALL_KEYS:
            return list(self.contents.values())
        # Returns a list of values for keys listed in `default` attribute.
        if key in configuration._DEFAULT_KEYS:
            if self.default in configuration._DEFAULT_KEYS:
                return list(self.contents.values())
            return self[self.default]
        # Returns a null value if a null value is sought.
        if key in configuration._NONE_KEYS:
            if self.default_factory is None:
                return [] if self.always_return_list else None
            return base.resolve_default(self.default_factory)
        # Returns matching value if `key` is stored directly in `contents`.
        try:
            if key in self.contents:
                value = self.contents[key]
                return [value] if self.always_return_list else value
        except TypeError:
            pass
        # Returns list of matching values if `key` is list-like.
        if isinstance(key, Sequence) and not isinstance(key, str):
            return [self.contents[k] for k in key if k in self.contents]
        raise KeyError(f"{key} is not in {self.__class__.__name__}")

    def __setitem__(
        self, key: Hashable | Sequence[Hashable], value: Any | Sequence[Any]
    ) -> None:
        """Sets `key` in `contents` to `value`.

        Args:
            key (Hashable | Sequence[Hashable]): key(s) to set in `contents`. If
                `key` is a list-like object that cannot be a key, each of its
                items is paired with the corresponding item in `value`.
            value (Any | Sequence[Any]): value(s) to be paired with `key` in
                `contents`.

        """
        try:
            self.contents[key] = value
        except TypeError:
            if isinstance(key, Sequence) and not isinstance(key, str):
                self.contents.update(zip(key, value, strict=True))
            else:
                raise


@dataclasses.dataclass
class ChainDictionary(Dictionary):
    """Combines functionality of collections.ChainMap with Dictionary.

    Keys are looked up in each stored mapping in order. The keys, values, and
    items of a ChainDictionary contain each key only once (using the value from
    the first mapping in which it appears). `len` returns the number of unique
    keys and iterating returns those keys.

    Attributes:
        contents (MutableSequence[MutableMapping[Hashable, Any]]): list of
            stored Dictionary instances (or other mappings). This is equivalent
            to the `maps` attribute of a collections.ChainMap instance but uses
            a different name for compatibility with base.Bunch. A separate
            `maps` property is included which points to `contents` to ensure
            compatibility in the opposite direction. Defaults to an empty list.
        default_factory (Any | None): default value to return or default
            callable to use to create the default value. Defaults to None.
        return_first (bool | None): whether to only return the first match found
            (True) or to search all of the stored mappings and return a list if
            more than one match is found (False). Defaults to True.

    """

    contents: MutableSequence[MutableMapping[Hashable, Any]] = (
        dataclasses.field(  # type: ignore[assignment]
            default_factory=list
        )
    )
    default_factory: Any | None = None
    return_first: bool | None = True

    # Properties

    @property
    def maps(self) -> MutableSequence[MutableMapping[Hashable, Any]]:
        """Returns `contents` attribute.

        Returns:
            MutableSequence[MutableMapping[Hashable, Any]]: stored mappings.

        """
        return self.contents

    @maps.setter
    def maps(
        self, value: MutableSequence[MutableMapping[Hashable, Any]]
    ) -> None:
        """Sets `contents` to `value`.

        Args:
            value (MutableSequence[MutableMapping[Hashable, Any]]): new
                list-like instance to assign `contents` to.

        """
        self.contents = value

    @maps.deleter
    def maps(self) -> None:
        """Sets `contents` to an empty list."""
        self.contents = []

    @property
    def parents(self) -> ChainDictionary:
        """Returns an instance with `contents` after the first.

        This property mirrors the functionality of collections.ChainMap.parents.

        Returns:
            ChainDictionary: an instance with all stored mappings after the
                first.

        """
        return dataclasses.replace(self, contents=list(self.contents[1:]))

    # Class Methods

    @classmethod
    def fromkeys(
        cls, keys: Iterable[Hashable], value: Any = None, **kwargs: Any
    ) -> Self:
        """Emulates the `fromkeys` class method from a python dict.

        Since this method is an awkward fit with a chained map, it just assigns
        the `keys` and `value` to a single Dictionary stored in the `contents`
        list.

        Args:
            keys (Iterable[Hashable]): items to be keys in a new Dictionary.
            value (Any): the value to use for all values in a new Dictionary.
                Defaults to None.
            **kwargs (Any): additional arguments to pass to the class
                constructor.

        Returns:
            ChainDictionary: formed from `keys` and `value`.

        """
        return cls(contents=[Dictionary.fromkeys(keys, value)], **kwargs)

    # Instance Methods

    def add(self, item: Mapping[Hashable, Any]) -> None:  # type: ignore[override]
        """Adds `item` to the end of the `contents` attribute.

        Args:
            item (Mapping[Hashable, Any]): mapping to add to `contents`
                attribute.

        Raises:
            TypeError: if `item` is not a mapping.

        """
        if not isinstance(item, MutableMapping):
            raise TypeError("item must be a MutableMapping")
        self.contents.append(item)

    def delete(self, item: Hashable) -> None:
        """Deletes `item` in `contents`.

        Because a chained mapping can have identical keys in different stored
        mappings, this method searches through all of the stored mappings and
        removes the key wherever it appears.

        Args:
            item (Hashable): key in `contents` to delete the key/value pair.

        Raises:
            KeyError: if `item` is not found in any stored mapping.

        """
        found = False
        for dictionary in self.contents:
            if item in dictionary:
                del dictionary[item]
                found = True
        if not found:
            raise KeyError(f"{item} is not found in the ChainDictionary")

    def items(self) -> tuple[tuple[Hashable, Any], ...]:  # type: ignore[override]
        """Emulates python dict `items` method.

        Returns:
            tuple[tuple[Hashable, Any], ...]: a tuple equivalent to
                dict.items().

        """
        return tuple((k, self._first_match(k)) for k in self.keys())

    def keys(self) -> tuple[Hashable, ...]:  # type: ignore[override]
        """Returns the unique keys in `contents` as a tuple.

        Returns:
            tuple[Hashable, ...]: a tuple equivalent to dict.keys().

        """
        return tuple(
            dict.fromkeys(itertools.chain.from_iterable(self.contents))
        )

    def new_child(
        self, m: MutableMapping[Hashable, Any] | None = None, **kwargs: Any
    ) -> None:
        """Inserts `m` as the first mapping in `contents`.

        This method mirrors the functionality and parameters of
        collections.Chainmap.new_child, except that it changes this instance
        instead of returning a new one.

        Args:
            m (MutableMapping[Hashable, Any] | None): new mapping to add to
                `contents` at index 0. If None, a new Dictionary is created.
                Defaults to None.
            **kwargs (Any): key/value pairs to add to `m`.

        """
        child: MutableMapping[Hashable, Any] = Dictionary() if m is None else m
        child.update(kwargs)
        self.contents.insert(0, child)

    def subset(  # type: ignore[override]
        self,
        include: Hashable | Sequence[Hashable] | None = None,
        exclude: Hashable | Sequence[Hashable] | None = None,
    ) -> Self:
        """Returns a new instance with a subset of `contents`.

        This method applies `include` before `exclude` if both are passed. If
        `include` is None, all existing items will be added to the new subset
        class instance before `exclude` is applied. The subset is applied to
        each of the stored mappings.

        Args:
            include (Hashable | Sequence[Hashable] | None): key(s) to include in
                the new instance. Defaults to None.
            exclude (Hashable | Sequence[Hashable] | None): key(s) to exclude
                from the new instance. Defaults to None.

        Raises:
            ValueError: if `include` and `exclude` are both None.

        Returns:
            ChainDictionary: with only keys from `include` and no keys in
                `exclude`.

        """
        contents = [
            Dictionary(_subset_mapping(d, include, exclude))
            for d in self.contents
        ]
        return dataclasses.replace(self, contents=contents)  # type: ignore[arg-type]

    def values(self) -> tuple[Any, ...]:  # type: ignore[override]
        """Returns `contents` values as a tuple.

        Returns:
            tuple[Any, ...]: a tuple equivalent to dict.values().

        """
        return tuple(self._first_match(k) for k in self.keys())

    # Private Methods

    def _first_match(self, key: Hashable) -> Any:
        """Returns the value for `key` in the first mapping that includes it.

        Args:
            key (Hashable): key for which a value is sought.

        Raises:
            KeyError: if `key` is not in any stored mapping.

        Returns:
            Any: value stored for `key` in the first mapping with `key`.

        """
        for dictionary in self.contents:
            if key in dictionary:
                return dictionary[key]
        raise KeyError(f"{key} is not found in the ChainDictionary")

    # Dunder Methods

    def __contains__(self, item: object) -> bool:
        """Returns whether `item` is a key in any stored mapping.

        Args:
            item (object): key to look for.

        Returns:
            bool: whether `item` is a key in any of the stored mappings.

        """
        return any(item in d for d in self.contents)

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value(s) for `key` in `contents`.

        If there are multiple matches for `key` and the `return_first` attribute
        is False, this method returns all matches in a list. Otherwise, only the
        first match is returned.

        Args:
            key (Hashable): key in `contents` for which a value is sought.

        Raises:
            KeyError: if `key` is not found in any stored mapping.

        Returns:
            Any: value(s) stored in `contents`.

        """
        if self.return_first:
            return self._first_match(key)
        matches = [d[key] for d in self.contents if key in d]
        if not matches:
            raise KeyError(f"{key} is not found in the ChainDictionary")
        return matches if len(matches) > 1 else matches[0]

    def __iter__(self) -> Iterator[Hashable]:
        """Returns an iterator of the unique keys in `contents`.

        Returns:
            Iterator[Hashable]: of the unique keys in `contents`.

        """
        return iter(self.keys())

    def __len__(self) -> int:
        """Returns the number of unique keys in `contents`.

        Returns:
            int: number of unique keys in `contents`.

        """
        return len(self.keys())

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        This method stores the passed `key` and `value` in the first stored
        mapping. If none exists, a Dictionary is created to store `key` and
        `value`.

        Args:
            key (Hashable): key to set in `contents`.
            value (Any): value to be paired with `key` in `contents`.

        """
        if not self.contents:
            self.contents = [Dictionary({key: value})]
        else:
            self.contents[0][key] = value


@dataclasses.dataclass
class Repository(Dictionary):
    """Dictionary with inferred keys based on items added.

    A Repository differs from an ordinary python dict in ways inherited from
    Dictionary. In addition, it differs in 2 other significant ways:
        1) The `add` method relies on the internal `_get_name` method to
            assign a str key for the passed item.
        2) It includes an `overwrite` parameter which allows users to determine
            whether existing items will be overwritten when the inferred key
            matches an existing one or whether a new key will be inferred by
            adding an integer counter as a suffix to the key.

    Attributes:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults to
            an empty dict.
        default_factory (Any | None): default value to return or default
            callable to use to create the default value. Defaults to None.
        overwrite (bool | None): whether to overwrite existing items in the
            stored dictionary with the same inferred keys (True) or
            automatically infer a new key based upon a counter suffix (False).
            Defaults to False.

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory=dict
    )
    default_factory: Any | None = None
    overwrite: bool | None = False

    # Instance Methods

    def add(self, item: Any, key: str | None = None) -> None:  # type: ignore[override]
        """Adds `item` to the `contents` attribute.

        Args:
            item (Any): item to add to `contents` attribute.
            key (str | None): key to use for `item` if the user does not want
                the key to be inferred. Defaults to None.

        """
        key = key or self._get_name(item=item)
        if not self.overwrite:
            key = modify.uniquify(key=key, dictionary=self.contents)
        self.contents[key] = item

    # Private Methods

    def _get_name(self, item: Any) -> str:
        """Infers key name for `item`.

        By default, this method uses the global key namer, which is the `namify`
        function in camina unless it has been changed by `set_key_namer`.
        Override this method to use a different naming function.

        Args:
            item (Any): item to infer the name for.

        Returns:
            str: inferred name.

        """
        return str(label.get_key_namer()(item))
