"""Flexible, lightweight, extensible, easy-to-use data structures and types"""

from __future__ import annotations

__version__ = '0.1.16'

__author__: str = 'Corey Rayburn Yung'

__all__: list[str] = []


from .base import Base, Descriptor, Proxy
from .clock import how_soon_is_now, timer
from .configuration import set_key_namer, set_method_namer
from .convert import (
    dictify,
    hashify,
    instancify,
    integerify,
    iterify,
    kwargify,
    listify,
    namify,
    numify,
    pathlibify,
    stringify,
    tuplify,
    typify,
    windowify,
)
from .label import Name, namify
from .mapping import Catalog, ChainDictionary, Dictionary, Repository
from .modify import (
    add_prefix,
    add_prefix_to_dict,
    add_prefix_to_list,
    add_prefix_to_set,
    add_prefix_to_str,
    add_prefix_to_tuple,
    add_slots,
    add_suffix,
    add_suffix_to_dict,
    add_suffix_to_list,
    add_suffix_to_set,
    add_suffix_to_str,
    add_suffix_to_tuple,
    capitalify,
    cleave,
    cleave_str,
    deduplicate,
    deduplicate_list,
    deduplicate_tuple,
    drop_dunders,
    drop_dunders_dict,
    drop_dunders_list,
    drop_prefix,
    drop_prefix_from_dict,
    drop_prefix_from_list,
    drop_prefix_from_set,
    drop_prefix_from_str,
    drop_prefix_from_tuple,
    drop_privates,
    drop_privates_dict,
    drop_privates_list,
    drop_substring,
    drop_substring_from_dict,
    drop_substring_from_list,
    drop_substring_from_set,
    drop_substring_from_str,
    drop_substring_from_tuple,
    drop_suffix,
    drop_suffix_from_dict,
    drop_suffix_from_list,
    drop_suffix_from_set,
    drop_suffix_from_str,
    drop_suffix_from_tuple,
    separate,
    separate_str,
    snakify,
    uniquify,
)
from .sequence import Hashable, Listing
