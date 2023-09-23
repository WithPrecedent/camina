# camina

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/camina.svg?style=for-the-badge&color=steelblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/camina/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/camina?style=for-the-badge&color=navy&label=GitHub&logo=github)](https://github.com/WithPrecedent/camina/releases)
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/camina/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/camina/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/camina?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/camina/)
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=navy&logo=github)](https://WithPrecedent.github.io/camina)
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/PDM-mediumpurple?style=for-the-badge&logo=affinity&labelColor=gray)](https://PDM.fming.dev) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-navy?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/camina) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-navy?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot)
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/camina?style=for-the-badge&color=steelblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/camina/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-snow?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/) [![Windows](https://img.shields.io/badge/windows-blue?style=for-the-badge&logo=Windows&labelColor=gray&color=orangered)](https://www.microsoft.com/en-us/windows?r=1)
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/camina?style=for-the-badge&color=steelblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/camina) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/camina?style=for-the-badge&color=navy&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/camina/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/camina?style=for-the-badge&color=navy&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/camina/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/camina?style=for-the-badge&color=navy&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/camina/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/camina?style=for-the-badge&color=navy&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/camina/forks)
| | |

-----

## What is camina?

This package adds functionality to core Python container classes and provides functions for common tasks.

## Why use camina?

## Mappings
* `Dictionary`: drop-in replacement for a python dict with an `add` method for a default mechanism of adding data, a `delete` method for a default mechanism of deleting data, and a `subset` method for returning a subset of the key/value pairs in a new `Dictionary`.
* `Catalog`: wildcard-accepting dict which is intended for storing different options and strategies. It also returns lists of matches if a list of keys is provided.
* `Library`: a dictionary that automatically supplies key names for stored items. The 'overwrite' argument determines if a unique key should always be created or whether entries may be overwritten.

### Sequences
* `Listing`: drop-in replacement for a python list with an `add` method for a default mechanism of adding data, a `delete` method for a default mechanism of deleting data, and a `subset` method for returning a subset of the key/value pairs in a new `Listing`.
* `Hybrid`: iterable with both dict and list interfaces. Stored items must be hashable or have a `name` attribute.

### Passthrough
* `Proxy`: transparently wraps an object and directs access methods to access the wrapped object when appropriate (under construction for edge cases).

### Converters

* `instancify`: converts a class to an instance or adds kwargs to a passed instance as attributes.
* `listify`: converts passed item to a list.
* `namify`: returns hashable name for passed item.
* `numify`: attempts to convert passed item to a numerical type.
* `pathlibify`: converts a str to a pathlib object or leaves it as a pathlib object.
* `stringify`:
* `tuplify`: converts a passed item to a tuple.
* `typify`: converts a str type to other common types, if possible.
* `windowify`:
* `to_dict`:
* `to_index`:
* `str_to_index`:
* `to_int`:
* `str_to_int`:
* `float_to_int`:
* `to_list`:
* `str_to_list`:
* `to_float`:
* `int_to_float`:
* `str_to_float`:
* `to_path`:
* `str_to_path`:
* `to_str`:
* `int_to_str`:
* `float_to_str`:
* `list_to_str`:
* `none_to_str`:
* `path_to_str`:
* `datetime_to_str`:

### Modifiers

* Adders:
  * `add_prefix`: adds a str prefix to item.
  * `add_slots`: adds `__slots__` to a dataclass.
  * `add_suffix`: adds a str suffix to item.
* Dividers:
  * `cleave`: divides an item into 2 parts based on `divider` argument.
  * `separate`: divides an item into n+1 parts based on `divider` argument.
* Subtractors:
  * `deduplicate`: removes duplicate data from an item.
  * `drop_dunders`: drops strings from a list if they start and end with double underscores.
  * `drop_prefix`: removes a str prefix from an item.
  * `drop_prefix_from_dict`
  * `drop_prefix_from_list`
  * `drop_prefix_from_set`
  * `drop_prefix_from_str`
  * `drop_prefix_from_tuple`
  * `drop_privates`
  * `drop_substring`: removes a substring from an item.
  * `drop_suffix`: removes a str suffix from an item.
  * `drop_suffix_from_dict`
  * `drop_suffix_from_list`
  * `drop_suffix_from_set`
  * `drop_suffix_from_str`
  * `drop_suffix_from_tuple`
* Other:
  * `capitalify`: converts a snake case str to capital case.
  * `snakify`: converts a capital case str to snake case.
  * `uniquify`: returns a unique key for a dict.

## Getting started

### Requirements

[TODO: List any OS or other restrictions and pre-installation dependencies]

### Installation

To install `camina`, use `pip`:

```sh
pip install camina
```

### Usage

[TODO: Describe common use cases, with possible example(s)]

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/camina/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/camina/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/camina/code_of_conduct.md).

## Similar Projects

[TODO: If they exist, it is always nice to acknowledge other similar efforts]

## Acknowledgments

[TODO: Mention any people or organizations that warrant a special acknowledgment]

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/camina/blog/main/LICENSE).
