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

`camina` provides functions for common tasks with Python data. It has three parts:

* **Converters**: functions that turn one type into another (`listify`, `tuplify`, `numify`, `pathlibify`, and more).
* **Modifiers**: functions that change the contents of strings, lists, tuples, sets, and dicts without changing their types (`add_prefix`, `drop_suffix`, `snakify`, and more).
* **Naming and time tools**: `namify` infers names for objects, and `how_soon_is_now` and `timer` handle timestamps and timing.

`camina` is fully typed, has no dependencies, and supports Python 3.11 and later.

## Why use camina?

* **Small, dependable helpers.** The converters and modifiers work on many types through `functools.singledispatch`, so you can also register your own types or call the type-specific versions directly.
* **Types are kept.** Modifiers return the same type they were given (a `list` stays a `list`, an `OrderedDict` stays an `OrderedDict`) and never change what you pass in.
* **Forgiving inputs.** Functions like `listify` and `iterify` let your own functions accept "one item or many" arguments without special cases.

Reasons *not* to use `camina`: most of these helpers are only a few lines of Python, so if you need just one of them, copying it may be simpler than adding a dependency.

## Features

### Converters

Except where noted, these live in the top-level `camina` namespace. The single-purpose `to_*` family (listed below) lives in `camina.convert`.

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

* `how_soon_is_now`: returns the current date and time as a str.
* `timer`: decorator that reports how long the decorated function takes to run.
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

#### Converters

```pycon
>>> import camina
>>> import dataclasses
>>> @dataclasses.dataclass
... class Settings:
...     name: str = "default"
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
>>> camina.namify(Settings), camina.namify(Settings("x")), camina.namify("y")
('settings', 'x', 'y')
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

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/camina/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/camina/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/camina/code_of_conduct.md).

## Similar Projects

* [boltons](https://github.com/mahmoud/boltons): a large collection of pure-Python utilities, including `iterutils` and `dictutils`.
* [more-itertools](https://github.com/more-itertools/more-itertools): additional building blocks for iterators. `camina.windowify` is adapted from its `windowed` function.
* [toolz](https://github.com/pytoolz/toolz): functional utilities for iterators, functions, and dictionaries.

## Acknowledgments

* Eric V. Smith, whose `dataclass_tools` recipe is the basis of `add_slots`.
* The maintainers of `more-itertools`, for the algorithm behind `windowify`.

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/camina/blob/main/LICENSE).
