# camina

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/camina.svg?style=for-the-badge&color=cornflowerblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/camina/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/camina?style=for-the-badge&color=forestgreen&label=GitHub&logo=github)](https://github.com/WithPrecedent/camina/releases) |
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/camina/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/camina/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/camina?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/camina/) |
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=forestgreen&logo=github)](https://WithPrecedent.github.io/camina) |
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/uv-mediumpurple?style=for-the-badge&logo=uv&labelColor=gray)](https://docs.astral.sh/uv/) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-forestgreen?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-forestgreen?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot) |
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/camina?style=for-the-badge&color=cornflowerblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/camina/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-antiquewhite?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/)  [![Windows](https://img.shields.io/badge/Windows-blue?style=for-the-badge)](https://www.microsoft.com/en-us/windows?r=1) |
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/camina?style=for-the-badge&color=cornflowerblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/camina) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/camina?style=for-the-badge&color=forestgreen&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/camina/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/camina?style=for-the-badge&color=forestgreen&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/camina/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/camina?style=for-the-badge&color=forestgreen&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/camina/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/camina?style=for-the-badge&color=forestgreen&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/camina/forks) |
| | |

-----

## What is camina?

*"Truth is truth. How you deal with it is up to you."* - Captain Camina Drummer

`camina` adds functionality to core Python container classes and provides functions for common tasks. It has three parts:

* **Containers**: drop-in replacements for `dict` and `list` (plus a few specialized cousins) that share a small, consistent interface: `add`, `delete`, and `subset`.
* **Converters**: functions that turn one type into another (`listify`, `tuplify`, `numify`, `pathlibify`, and more).
* **Modifiers**: functions that change the contents of strings, lists, tuples, sets, and dicts without changing their types (`add_prefix`, `drop_suffix`, `snakify`, and more).

`camina` is fully typed, has no dependencies, and supports Python 3.11 and later.

## Why use camina?

* **One interface for many containers.** Every container in `camina` inherits from `Bunch`, so `add` is always the default way to put something in, `delete` the default way to take something out, and `subset` the default way to carve out a piece as a new container of the same type. The `+` and `+=` operators call `add`.
* **Flexible lookups.** A `Catalog` understands wildcard keys (`"all"`, `"default"`, `"none"`) and lists of keys, which makes it a natural home for options and strategies. A `Hybrid` lets you use one collection as both a list and a dict, even with duplicate "keys".
* **Names for free.** A `Repository` picks the keys for the items you store, and can guarantee that it never overwrites an existing item.
* **Small, dependable helpers.** The converters and modifiers work on many types through `functools.singledispatch`, so you can also register your own types or call the type-specific versions directly.

Reasons *not* to use `camina`: if you only need the built-in containers, adding a dependency buys you little. Some behaviors intentionally differ from the built-ins (for example, `Dictionary.get` raises a `KeyError` when a key is missing and no default exists, and `keys()`, `values()`, and `items()` return tuples), so `camina` containers are best treated as friendly cousins rather than exact clones.

## Features

### Containers

All of these are dataclasses that store their data in a `contents` attribute.

* `Bunch`: abstract base class for the containers below. Subclasses must provide `add`, `delete`, and `subset`.
* `Dictionary`: drop-in replacement for a python `dict`. It has an `add` method for adding data, a `delete` method for deleting data, a `subset` method for returning a subset of the key/value pairs in a new `Dictionary`, and a `default_factory` (a default value or a callable that creates one) that `get` uses for missing keys.
* `Catalog`: wildcard-accepting `Dictionary` intended for storing different options and strategies. The keys `"all"`, `"default"`, and `"none"` return all values, the values listed in the `default` attribute, and nothing, respectively. If a list of keys is provided, a list of the matching values is returned.
* `ChainDictionary`: combines a `Dictionary` with `collections.ChainMap`. Keys are looked up in a list of mappings, in order.
* `Repository`: a `Dictionary` that automatically supplies key names for stored items. The `overwrite` argument determines if a unique key should always be created or whether entries may be overwritten.
* `Listing`: drop-in replacement for a python `list` with `add`, `delete`, `prepend`, and `subset` methods.
* `Hybrid`: a `Listing` with both dict and list interfaces. Stored items must be hashable or have a `name` attribute.
* `Proxy`: transparently wraps an object and directs attribute and item access to the wrapped object when appropriate.
* `Descriptor`: base class for descriptors that stores values under a private name.
* `Name`: descriptor that supplies an inferred `name` attribute to an object.

### Converters

Except where noted, these live in the top-level `camina` namespace. The `to_*` family (listed below) lives in `camina.convert`.

* `dictify`: converts to or validates a dict.
* `hashify`: converts to or validates a hashable object.
* `instancify`: converts a class to an instance or adds kwargs to a passed instance as attributes.
* `integerify`: converts to or validates an int.
* `iterify`: returns an iterable without iterating over str types.
* `kwargify`: uses annotations to turn positional arguments into keyword arguments.
* `listify`: converts passed item to a list.
* `namify`: returns a name for the passed item.
* `numify`: attempts to convert passed item to a numerical type.
* `pathlibify`: converts a str to a `pathlib.Path` or leaves it as a `pathlib.Path`.
* `stringify`: converts a sequence to a str.
* `tuplify`: converts a passed item to a tuple.
* `typify`: converts a str to another common type (int, float, bool, or list), if possible.
* `windowify`: returns a sliding window of a given length over an iterable.

The `camina.convert` module also includes single-purpose converters. `to_dict`, `to_index`, `to_int`, `to_list`, `to_float`, `to_path`, and `to_str` convert to their respective types and dispatch on the type of the passed item. The type-specific functions they use can be called directly:

* `str_to_index`, `str_to_int`, `float_to_int`
* `str_to_list`
* `int_to_float`, `str_to_float`
* `str_to_path`
* `int_to_str`, `float_to_str`, `list_to_str`, `none_to_str`, `path_to_str`, `datetime_to_str`

### Modifiers

Each modifier below is a `functools.singledispatch` function that supports `str`, `dict`, `list`, `set`, and `tuple` types (unless noted). The type-specific versions are named by adding `_to_` or `_from_` and the type (for example, `add_prefix_to_str` and `drop_prefix_from_dict`).

* Adders:
  * `add_prefix`: adds a str prefix to item. Also available: `add_prefix_to_dict`, `add_prefix_to_list`, `add_prefix_to_set`, `add_prefix_to_str`, and `add_prefix_to_tuple`.
  * `add_slots`: adds `__slots__` to a dataclass.
  * `add_suffix`: adds a str suffix to item. Also available: `add_suffix_to_dict`, `add_suffix_to_list`, `add_suffix_to_set`, `add_suffix_to_str`, and `add_suffix_to_tuple`.
* Dividers:
  * `cleave`: divides a str into 2 parts based on `divider`. Also available: `cleave_str`.
  * `separate`: divides a str into n+1 parts based on `divider`. Also available: `separate_str`.
* Subtractors:
  * `deduplicate`: removes duplicate data from a list or tuple. Also available: `deduplicate_list` and `deduplicate_tuple`.
  * `drop_dunders`: drops strings (or the names of items) that start and end with double underscores. Also available: `drop_dunders_dict`, `drop_dunders_list`, `drop_dunders_set`, and `drop_dunders_tuple`.
  * `drop_prefix`: removes a str prefix from an item. Also available: `drop_prefix_from_dict`, `drop_prefix_from_list`, `drop_prefix_from_set`, `drop_prefix_from_str`, and `drop_prefix_from_tuple`.
  * `drop_privates`: drops strings (or the names of items) that start with an underscore. Also available: `drop_privates_dict`, `drop_privates_list`, `drop_privates_set`, and `drop_privates_tuple`.
  * `drop_substring`: removes a substring from an item. Also available: `drop_substring_from_dict`, `drop_substring_from_list`, `drop_substring_from_set`, `drop_substring_from_str`, and `drop_substring_from_tuple`.
  * `drop_suffix`: removes a str suffix from an item. Also available: `drop_suffix_from_dict`, `drop_suffix_from_list`, `drop_suffix_from_set`, `drop_suffix_from_str`, and `drop_suffix_from_tuple`.
* Other:
  * `capitalify`: converts a snake case str to capital case.
  * `snakify`: converts a capital case str to snake case.
  * `uniquify`: returns a unique key for a dict.

### Other tools

* `resolve_default`: returns a default value, calling it first if it is callable. The containers use it for their `default_factory` attribute.
* `how_soon_is_now`: returns the current date and time as a str.
* `timer`: decorator that reports how long the decorated function takes to run.
* `set_key_namer` and `get_key_namer`: set and get the global function used to infer names (keys) for items. `Repository`, `Hybrid`, and `Name` use it.
* `set_method_namer` and `get_method_namer`: set and get the global function used to name factory methods.

## Getting started

### Requirements

`camina` requires Python 3.11 or later. It has no third-party dependencies and runs on Linux, macOS, and Windows.

### Installation

To install `camina`, use `pip`:

```sh
pip install camina
```

### Usage

The examples below are run as part of the test suite, so they are always up to date.

#### Dictionaries

A `Dictionary` behaves like a `dict`, but adds `add`, `delete`, `subset`, and a default value for `get`:

```pycon
>>> import camina
>>> dictionary = camina.Dictionary({"a": 1, "b": 2})
>>> dictionary.add({"c": 3})
>>> dictionary.subset(include=["a", "c"]).keys()
('a', 'c')
>>> dictionary.subset(exclude="a").contents
{'b': 2, 'c': 3}
>>> dictionary.get("missing", 0)
0
>>> dictionary.setdefault(value=None)
>>> dictionary.delete("b")
>>> dictionary.contents
{'a': 1, 'c': 3}
```

A `Catalog` recognizes wildcard keys and lists of keys:

```pycon
>>> catalog = camina.Catalog({"linear": "LinearModel", "tree": "TreeModel"})
>>> catalog["linear"]
'LinearModel'
>>> catalog["all"]
['LinearModel', 'TreeModel']
>>> catalog[["tree", "linear"]]
['TreeModel', 'LinearModel']
>>> catalog.default = ["tree"]
>>> catalog["default"]
['TreeModel']
>>> catalog["none"] is None
True
```

A `Repository` chooses the keys for you and, by default, never overwrites an existing item:

```pycon
>>> repository = camina.Repository()
>>> repository.add(camina.Dictionary())
>>> repository.add(camina.Dictionary())
>>> repository.add([1, 2], key="numbers")
>>> repository.keys()
('dictionary', 'dictionary2', 'numbers')
```

A `ChainDictionary` searches several mappings in order:

```pycon
>>> chain = camina.ChainDictionary([{"a": 1}, {"a": 2, "b": 3}])
>>> chain["a"], chain["b"]
(1, 3)
>>> chain.keys()
('a', 'b')
```

#### Lists

A `Listing` is a `list` that can `add` a single item or a whole sequence and can `prepend`:

```pycon
>>> listing = camina.Listing(["a", "b"])
>>> listing.add(["c", "d"])
>>> listing.prepend("z")
>>> listing.contents
['z', 'a', 'b', 'c', 'd']
>>> listing.subset(exclude=["z", "d"]).contents
['a', 'b', 'c']
>>> (listing + "e").contents[-1]
'e'
```

A `Hybrid` is a list that can also be used like a dict. Items are found by index or by name (their `name` attribute, or the item itself if it is a str or other hashable):

```pycon
>>> import dataclasses
>>> @dataclasses.dataclass
... class Step:
...     name: str
>>> hybrid = camina.Hybrid([Step("load"), Step("clean"), "save"])
>>> hybrid[0]
Step(name='load')
>>> hybrid["clean"]
Step(name='clean')
>>> hybrid.keys()
('load', 'clean', 'save')
```

#### Proxies and descriptors

A `Proxy` forwards attribute and item access to the object it wraps:

```pycon
>>> @dataclasses.dataclass
... class Settings:
...     name: str = "default"
>>> settings = Settings()
>>> proxy = camina.Proxy(settings)
>>> proxy.name
'default'
>>> proxy.name = "changed"
>>> settings.name
'changed'
>>> "changed" in camina.Proxy(["changed"])
True
```

A `Name` descriptor gives a class a `name` that is inferred from the class unless a name is stored:

```pycon
>>> class Widget:
...     name = camina.Name()
>>> widget = Widget()
>>> widget.name
'widget'
>>> widget.name = "custom"
>>> widget.name
'custom'
```

#### Converters

```pycon
>>> camina.listify("a"), camina.listify(("a", "b")), camina.listify(None)
(['a'], ['a', 'b'], [])
>>> camina.tuplify("ab"), camina.tuplify(["a", "b"])
(('ab',), ('a', 'b'))
>>> camina.numify("3"), camina.numify("3.5"), camina.numify("three")
(3, 3.5, 'three')
>>> camina.typify("yes"), camina.typify("1, 2.5, no")
(True, [1, 2.5, False])
>>> camina.stringify(["a", "b"])
'a, b'
>>> camina.pathlibify("docs/index.md").name
'index.md'
>>> camina.namify(dictionary), camina.namify(Step("x")), camina.namify(Widget)
('dictionary', 'x', 'widget')
>>> list(camina.windowify([1, 2, 3, 4], length=3))
[(1, 2, 3), (2, 3, 4)]
>>> camina.instancify(Settings, name="new")
Settings(name='new')
>>> camina.kwargify(Settings, ("positional",))
{'name': 'positional'}
>>> camina.convert.to_list("[1, 2]")
[1, 2]
```

#### Modifiers

```pycon
>>> camina.add_prefix(["a", "b"], "pre", divider="_")
['pre_a', 'pre_b']
>>> camina.add_suffix({"a": 1}, "post", divider="_")
{'a_post': 1}
>>> camina.drop_prefix(["pre_a", "pre_b"], "pre", divider="_")
['a', 'b']
>>> camina.drop_suffix("name_post", "post", divider="_")
'name'
>>> camina.drop_substring(("abc", "cba"), "b")
('ac', 'ca')
>>> camina.drop_privates(["_hidden", "shown", "__dunder__"])
['shown']
>>> camina.drop_dunders(["_hidden", "shown", "__dunder__"])
['_hidden', 'shown']
>>> camina.cleave("a_b_c"), camina.cleave("a_b_c", return_last=False)
(('a_b', 'c'), ('a', 'b_c'))
>>> camina.separate("a_b_c")
['a', 'b', 'c']
>>> camina.deduplicate([1, 2, 1, 3, 2])
[1, 2, 3]
>>> camina.snakify("HTTPServerError"), camina.capitalify("http_server_error")
('http_server_error', 'HttpServerError')
>>> camina.uniquify("name", {"name": 1, "name2": 2})
'name3'
>>> Slotted = camina.add_slots(Settings)
>>> Slotted.__slots__
('name',)
```

#### Clock

```pycon
>>> camina.how_soon_is_now(prefix="run_")  # doctest: +ELLIPSIS
'run_...'
>>> @camina.timer
... def work():
...     return "done"
>>> work()
work completed in 0:00:00
'done'
```

#### Configuration

`Repository`, `Hybrid`, and `Name` infer names with `camina.namify` unless you set a different function:

```pycon
>>> camina.set_key_namer(lambda item: type(item).__name__.upper())
>>> repository = camina.Repository()
>>> repository.add(3.5)
>>> repository.keys()
('FLOAT',)
>>> camina.set_key_namer(None)  # Restores camina.namify.
```

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/camina/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/camina/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/camina/code_of_conduct.md).

## Similar Projects

* [boltons](https://github.com/mahmoud/boltons): a large collection of pure-Python utilities, including `iterutils` and `dictutils`.
* [more-itertools](https://github.com/more-itertools/more-itertools): additional building blocks for iterators. `camina.windowify` is adapted from its `windowed` function.
* [toolz](https://github.com/pytoolz/toolz): functional utilities for iterators, functions, and dictionaries.
* [sortedcontainers](https://github.com/grantjenks/python-sortedcontainers): sorted list, set, and dict types.

## Acknowledgments

* The Python core developers, whose [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html) informed the `Descriptor` class.
* Eric V. Smith, whose `dataclass_tools` recipe is the basis of `add_slots`.
* The maintainers of `more-itertools`, for the algorithm behind `windowify`.

This project was generated from [@WithPrecedent](https://github.com/WithPrecedent)'s [![cookiecutter Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) template.

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/camina/blob/main/LICENSE).
