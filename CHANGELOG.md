# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.2.1

### Changed

* README examples are easier to read: one call per line, grouped by task, and without `>>>` prompts.

## 0.2.0

### Added

* The `to_*` converters in `camina.convert` that the README described.
* `drop_dunders` and `drop_privates` for sets and tuples.
* A full test suite (including tests that run the README examples), docs pages, and typed `Args` in all docstrings.

### Changed

* Updated to snickerdoodle v0.3.3: `uv` and `hatchling` replace `pdm`, workflows were consolidated, and `mypy` and `pydoclint` are used in CI.
* Dropped support for Python 3.10. Python 3.11 or later is required.
* `miller` is no longer a dependency. It depended on `camina`, which made a circular dependency.
* `listify` and `tuplify` convert non-str collections (tuples, sets, generators, etc.) and no longer split strings.
* `drop_dunders` only drops names that both start and end with double underscores.
* `iterify` returns its input if it is already iterable.

### Removed

* The container classes (`Bunch`, `Dictionary`, `Catalog`, `ChainDictionary`, `Repository`, `Listing`, `Hybrid`, `Proxy`, `Descriptor`, and `Name`) and their helpers (`resolve_default`, `set_key_namer`, `get_key_namer`, `set_method_namer`, and `get_method_namer`). They now live in the separate `bunches` package.

### Fixed

* `import camina` failed because `camina.__init__` imported a nonexistent `Base` class.
* `how_soon_is_now` raised an error (`tz_info` argument), and `timer` could not be used as a decorator.
* `cleave` split incorrectly when `return_last` was False; `uniquify` and `drop_suffix` (with a divider) returned wrong results.
* `numify` raised on `None` and truncated floats; `tuplify` split strings; `pathlibify` failed on strings; `windowify` did not validate arguments until iterated.
* `add_slots` failed for classes with a `__weakref__` slot.

## 0.1.0

    Initial Commit
