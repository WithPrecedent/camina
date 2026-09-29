# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## Unreleased

### Added

* `Bunch` (replacing the nonexistent `Base` in the imports of `camina.__init__`) and `Hybrid` are now exported, and `Hybrid` validates the items it stores.
* `Proxy` now handles setting and deleting attributes, item access, iteration, length, and calls.
* `Dictionary.popitem`, `ChainDictionary.parents` (now a property), and `ChainDictionary.new_child(**kwargs)`.
* `Listing` and `Hybrid` slices return the same type as the original.
* `drop_dunders` and `drop_privates` for sets and tuples.
* `get_key_namer`, `get_method_namer`, `resolve_default`, and the `to_*` converters in `camina.convert` that the README described.
* A full test suite (including tests that run the README examples), docs pages, and typed `Args` in all docstrings.

### Changed

* Dropped support for Python 3.10. Python 3.11 or later is required.
* Updated to snickerdoodle v0.3.3: `uv` and `hatchling` replace `pdm`, workflows were consolidated, and `mypy` and `pydoclint` are used in CI.
* `miller` is no longer a dependency. It depended on `camina`, which made a circular dependency.
* `+` returns a new container instead of changing the original. Use `+=` to add in place.
* `Dictionary.subset` and `ChainDictionary.subset` ignore keys that are not present, and subsets no longer deep copy the container.
* `listify` and `tuplify` convert non-str collections (tuples, sets, generators, etc.) and no longer split strings.
* `drop_dunders` only drops names that both start and end with double underscores.
* `iterify` returns its input if it is already iterable.
* `Name` passes the owner's class to its `namer` and works as a dataclass field default.

### Fixed

* `import camina` failed because `camina.__init__` imported a nonexistent `Base` class.
* `how_soon_is_now` raised an error (`tz_info` argument), and `timer` could not be used as a decorator.
* `set_key_namer` set an unused global, so it had no effect.
* `cleave` split incorrectly when `return_last` was False; `uniquify` and `drop_suffix` (with a divider) returned wrong results.
* `ChainDictionary` returned lists for single matches, could not be iterated by key, and failed to `add` mappings.
* `Catalog.delete` replaced its `contents` and treated wildcards as existing keys.
* `numify` raised on `None` and truncated floats; `tuplify` split strings; `pathlibify` failed on strings; `windowify` did not validate arguments until iterated.
* `add_slots` failed for classes with a `__weakref__` slot.
* Dropped `Library` from the README (the class is named `Repository`) and removed stubs that described functions that did not exist.

## 0.1.0

    Initial Commit
