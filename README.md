[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/camina/badge/?version=latest)](http://camina.readthedocs.io/?badge=latest)


This package adds functionality to core Python container classes and provides functions for common tasks.

## Mappings
* `Dictionary`: drop-in replacement for a python dict with an `add` method for a default mechanism of adding data, a `delete` method for a default mechanism of deleting data, and a `subset` method for returning a subset of the key/value pairs in a new `Dictionary`.
* `Catalog`: wildcard-accepting dict which is intended for storing different options and strategies. It also returns lists of matches if a list of keys is provided.
* `Library`: a dictionary that automatically supplies key names for stored items. The 'overwrite' argument determines if a unique key should always be created or whether entries may be overwritten.

## Sequences
* `Listing`: drop-in replacement for a python list with an `add` method for a default mechanism of adding data, a `delete` method for a default mechanism of deleting data, and a `subset` method for returning a subset of the key/value pairs in a new `Listing`.
* `Hybrid`: iterable with both dict and list interfaces. Stored items must be hashable or have a `name` attribute.

## Passthrough
* `Proxy`: transparently wraps an object and directs access methods to access the wrapped object when appropriate (under construction for edge cases).

## Converters

* `instancify`: converts a class to an instance or adds kwargs to a passed instance as attributes.
* `listify`: converts passed item to a list.
* `namify`: returns hashable name for passed item.
* `numify`: attempts to convert passed item to a numerical type.
* `pathlibify`: converts a str to a pathlib object or leaves it as a pathlib object.
* `stringify`:
* `tuplify`: converts a passed item to a tuple.
* `typify`: converts a str type to other common types, if possible.
*  `windowify`:
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

## Modifiers
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

camina supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more funcitonal approaching to programming. 

The project is also highly internally documented so that users and developers can easily make camina work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.