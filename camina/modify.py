"""
modify: functions that modify stored data without changing the data type
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2023, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Adders:
        add_prefix (dispatcher): adds a str prefix to item.
        add_slots: adds '__slots__' to a dataclass.
        add_suffix (dispatcher): adds a str suffix to item.
    Dividers:
        cleave (dispatcher): divides an item into 2 parts based on
            'divider'.
        separate (dispatcher): divides an item into n+1 parts based on
            'divider'.
    Subtractors:
        deduplicate (dispatcher): removes duplicate data from an item.
        drop_dunders: drops strings from a list if they start and end with 
            double underscores.
        drop_prefix (dispatcher): removes a str prefix from an item.
        drop_prefix_from_dict
        drop_prefix_from_list
        drop_prefix_from_set
        drop_prefix_from_str
        drop_prefix_from_tuple
        drop_privates
        drop_substring (dispatcher): removes a substring from an item.
        drop_suffix (dispatcher): removes a str suffix from an item.
    Other: 
        capitalify: converts a snake case str to capital case.
        snakify: converts a capital case str to snake case.
        uniquify: returns a unique key for a dict.

ToDo:


"""
from __future__ import annotations

from collections.abc import Hashable, Mapping, MutableSequence, Sequence, Set
import dataclasses
import functools
import re
from typing import Any, Optional, Type


""" Adders """

@functools.singledispatch
def add_prefix(
    item: Any, /, 
    prefix: str, 
    divider: Optional[str] = '',
    recursive: Optional[bool] = False) -> Any:
    """Adds 'prefix' to 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (Optional[str]): str to add between 'item' and 'prefix'. 
            Defaults to '', which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        Any: modified item.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')
 
@add_prefix.register(str)
def add_prefix_to_str(
    item: str,
    prefix: str, 
    divider: Optional[str] = '',
    recursive: Optional[bool] = False) -> str:
    """Adds 'prefix' to 'item' with 'divider' in between.
    
    Args:
        item (str): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False. This argument has no effect
            if 'item' is a str type.
            
    Returns:
        str: modified str.

    """
    return divider.join([prefix, item])
 
@add_prefix.register(Mapping)
def add_prefix_to_dict(
    item: Mapping[str, Any], /,
    prefix: str, 
    divider: Optional[str] = '',
    recursive: Optional[bool] = False) -> Mapping[str, Any]:
    """Adds 'prefix' to keys in 'item' with 'divider' in between.
    
    Args:
        item (Mapping[str, Any]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
            
    Returns:
        Mapping[str, Any]: modified mapping.

    """
    base = type(item)
    kwargs = dict(prefix = prefix, divider = divider, recursive = recursive)
    if recursive:
        tool = add_prefix
    else:
        tool = add_prefix_to_str
    return base({tool(k, **kwargs): v for k, v in item.items()})
 
@add_prefix.register(MutableSequence)
def add_prefix_to_list(
    item: MutableSequence[str], /, 
    prefix: str, 
    divider: str = '',
    recursive: Optional[bool] = False) -> MutableSequence[str]:
    """Adds 'prefix' to items in 'item' with 'divider' in between.
    
    Args:
        item (MutableSequence[str]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
            
    Returns:
        Any: modified mutable sequence.

    """
    base = type(item)
    kwargs = dict(prefix = prefix, divider = divider, recursive = recursive)
    if recursive:
        tool = add_prefix
    else:
        tool = add_prefix_to_str
    return base([tool(i, **kwargs) for i in item])
 
@add_prefix.register(Set)
def add_prefix_to_set(
    item: Set[str], /, 
    prefix: str, 
    divider: str = '',
    recursive: Optional[bool] = False) -> Set[str]:
    """Adds 'prefix' to items in 'item' with 'divider' in between.
    
    Args:
        item (Set[str]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
            
    Returns:
        Set[str]: modified set.

    """
    base = type(item)
    kwargs = dict(prefix = prefix, divider = divider, recursive = recursive)
    if recursive:
        tool = add_prefix
    else:
        tool = add_prefix_to_str
    return base({tool(i, **kwargs) for i in item})

@add_prefix.register(tuple)
def add_prefix_to_tuple(
    item: tuple[str, ...], /, 
    prefix: str, 
    divider: str = '',
    recursive: Optional[bool] = False) -> tuple[str, ...]:
    """Adds 'prefix' to items in 'item' with 'divider' in between.
    
    Args:
        item (tuple[str, ...]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
              
    Returns:
        tuple[str, ...]: modified tuple.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
      
    """
    kwargs = dict(prefix = prefix, divider = divider, recursive = recursive)
    return tuple(add_prefix_to_list(item, **kwargs))

def add_slots(item: Type[Any]) -> Type[Any]:
    """Adds slots to dataclass with default values.
    
    Derived from code here: 
    https://gitquirks.com/ericvsmith/dataclasses/blob/master/dataclass_tools.py
    
    Args:
        item (Type[Any]): dataclass to add slots to.

    Returns:
        Type[Any]: class with '__slots__' added.
        
    Raises:
        TypeError: if '__slots__' is already in item.
                
    """
    if '__slots__' in item.__dict__:
        raise TypeError(f'{item.__name__} already contains __slots__')
    else:
        item_dict = dict(item.__dict__)
        field_names = tuple(f.name for f in dataclasses.fields(item))
        item_dict['__slots__'] = field_names
        for field_name in field_names:
            item_dict.pop(field_name, None)
        item_dict.pop('__dict__', None)
        qualname = getattr(item, '__qualname__', None)
        item = type(item)(item.__name__, item.__bases__, item_dict)
        if qualname is not None:
            item.__qualname__ = qualname
    return item

@functools.singledispatch
def add_suffix(
    item: Any, /, 
    suffix: str, 
    divider: Optional[str] = '',
    recursive: Optional[bool] = False) -> Any:
    """Adds 'suffix' to 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (Optional[str]): str to add between 'item' and 'suffix'. 
            Defaults to '', which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.

    Returns:
        Any: modified item.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')
 
@add_suffix.register(str)
def add_suffix_to_str(
    item: str,
    suffix: str, 
    divider: Optional[str] = '',
    recursive: Optional[bool] = False) -> str:
    """Adds 'suffix' to 'item' with 'divider' in between.
    
    Args:
        item (str): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (str): str to add between 'item' and 'suffix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False. This argument has no effect
            if 'item' is a str type.
            
    Returns:
        str: modified str.

    """
    return divider.join([item, suffix])
 
@add_suffix.register(Mapping)
def add_suffix_to_dict(
    item: Mapping[str, Any], /,
    suffix: str, 
    divider: Optional[str] = '',
    recursive: Optional[bool] = False) -> Mapping[str, Any]:
    """Adds 'suffix' to keys in 'item' with 'divider' in between.
    
    Args:
        item (Mapping[str, Any]): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (str): str to add between 'item' and 'suffix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
            
    Returns:
        Mapping[str, Any]: modified mapping.

    """
    base = type(item)
    kwargs = dict(suffix = suffix, divider = divider, recursive = recursive)
    if recursive:
        tool = add_suffix
    else:
        tool = add_suffix_to_str
    return base({tool(k, **kwargs): v for k, v in item.items()})
 
@add_suffix.register(MutableSequence)
def add_suffix_to_list(
    item: MutableSequence[str], /, 
    suffix: str, 
    divider: str = '',
    recursive: Optional[bool] = False) -> MutableSequence[str]:
    """Adds 'suffix' to items in 'item' with 'divider' in between.
    
    Args:
        item (MutableSequence[str]): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (str): str to add between 'item' and 'suffix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
            
    Returns:
        Any: modified mutable sequence.

    """
    base = type(item)
    kwargs = dict(suffix = suffix, divider = divider, recursive = recursive)
    if recursive:
        tool = add_suffix
    else:
        tool = add_suffix_to_str
    return base([tool(i, **kwargs) for i in item])
 
@add_suffix.register(Set)
def add_suffix_to_set(
    item: Set[str], /, 
    suffix: str, 
    divider: str = '',
    recursive: Optional[bool] = False) -> Set[str]:
    """Adds 'suffix' to items in 'item' with 'divider' in between.
    
    Args:
        item (Set[str]): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (str): str to add between 'item' and 'suffix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
            
    Returns:
        Set[str]: modified set.

    """
    base = type(item)
    kwargs = dict(suffix = suffix, divider = divider, recursive = recursive)
    if recursive:
        tool = add_suffix
    else:
        tool = add_suffix_to_str
    return base({tool(i, **kwargs) for i in item})

@add_suffix.register(tuple)
def add_suffix_to_tuple(
    item: tuple[str, ...], /, 
    suffix: str, 
    divider: str = '',
    recursive: Optional[bool] = False) -> tuple[str, ...]:
    """Adds 'suffix' to items in 'item' with 'divider' in between.
    
    Args:
        item (tuple[str, ...]): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (str): str to add between 'item' and 'suffix'. Defaults to '',
            which means no divider will be added.
        recursive (Optional[bool]: False): if 'item' is nested, whether to apply
            the function to all nested objects as well (True) or merely the top
            level object (False). Defaults to False.
              
    Returns:
        tuple[str, ...]: modified tuple.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
      
    """
    kwargs = dict(suffix = suffix, divider = divider, recursive = recursive)
    return tuple(add_suffix_to_list(item, **kwargs))

""" Dividers """

@functools.singledispatch
def cleave(
    item: Any, /, 
    divider: Any,
    return_last: bool = True,
    raise_error: bool = False) -> tuple[Any, Any]:
    """Divides 'item' into 2 parts based on 'divider'.

    Args:
        item (Any): item to be divided.
        divider (Any): item to divide 'item' upon.
        return_last (bool): whether to split 'item' upon the first (False) or
            last appearance of 'divider'.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        TypeError: if no registered function supports the type of 'item'. 
        
    Returns:
        tuple[Any, Any]: parts of 'item' on either side of 'divider' unless
            'divider' is not in 'item'.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@cleave.register
def cleave_str(
    item: str, /, 
    divider: str = '_',
    return_last: bool = True,
    raise_error: bool = False) -> tuple[str, str]:
    """Divides 'item' into 2 parts based on 'divider'.

    Args:
        item (str): item to be divided.
        divider (str): item to divide 'item' upon.
        return_last (bool): whether to split 'item' upon the first (False) or
            last appearance of 'divider'.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        ValueError: if 'divider' is not in 'item' and 'raise_error' is True.
        
    Returns:
        tuple[str, str]: parts of 'item' on either side of 'divider' unless
            'divider' is not in 'item'.
        
    """
    if divider in item:
        if return_last:
            suffix = item.split(divider)[-1]
        else:
            suffix = item.split(divider)[0]
        prefix = item[:-len(suffix) - 1]
    elif raise_error:
        raise ValueError(f'{divider} is not in {item}')
    else:
        prefix = suffix = item
    return prefix, suffix

@functools.singledispatch
def separate(
    item: Any, /, 
    divider: Any,
    raise_error: bool = False) -> tuple[Any, ...]:
    """Divides 'item' into n+1 parts based on 'divider'.

    Args:
        item (Any): item to be divided.
        divider (Any): item to divide 'item' upon.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        TypeError: if no registered function supports the type of 'item'. 
        
    Returns:
        list[Any, ...]: parts of 'item' on either side of 'divider' unless
            'divider' is not in 'item'.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@separate.register
def separate_str(
    item: str, /, 
    divider: str = '_',
    raise_error: bool = False) -> list[str]:
    """Divides 'item' into n+1 parts based on 'divider'.

    Args:
        item (str): item to be divided.
        divider (str): item to divide 'item' upon.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        ValueError: if 'divider' is not in 'item' and 'raise_error' is True.
        
    Returns:
        list[str]: parts of 'item' on either side of 'divider' unless 'divider' 
            is not in 'item'.
        
    """
    if divider in item:
        return item.split(divider)
    elif raise_error:
        raise ValueError(f'{divider} is not in {item}')
    else:
        return [item]
 
""" Subtractors """

@functools.singledispatch
def deduplicate(item: Any, /) -> Any:
    """Deduplicates contents of 'item.
    
    Args:
        item (Any): item to deduplicate.

    Raises:
        TypeError: if no registered function supports the type of 'item'.     
        
    Returns:
        Any: deduplicated item.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@deduplicate.register(MutableSequence)
def deduplicate_list(item: MutableSequence[Any], /) -> MutableSequence[Any]:
    """Deduplicates contents of 'item.
    
    Args:
        item (MutableSequence[Any]): item to deduplicate.

    Returns:
        MutableSequence[Any]: deduplicated item.
        
    """
    base = type(item)
    contents = list(dict.fromkeys(item))
    return base(contents)

@deduplicate.register(tuple)
def deduplicate_tuple(item: tuple[Any, ...], /) -> tuple[Any, ...]:
    """Deduplicates contents of 'item.
    
    Args:
        item (tuple[Any, ...]): item to deduplicate.

    Returns:
        tuple[Any, ...]: deduplicated item.
        
    """
    return tuple(deduplicate_list(item))
    
@functools.singledispatch
def drop_dunders(item: Any, /) -> Any:
    """Drops items in 'item' beginning with a double underscore.

    Args:
        item (Any): item to modify.

    Returns:
        Any: item with entries dropped beginning with a double underscore.
        
    Raises:
        TypeError: if 'item' is not a registered type.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_dunders.register(Mapping)
def drop_dunders_dict(item: Mapping[str, Any], /) -> Mapping[str, Any]:
    """Drops items in 'item' beginning with a double underscore.

    Args:
        item (Mapping[str, Any]): dict-like object with str keys that might have
            double underscores at the beginning of the key names.

    Returns:
        Mapping[str, Any]: dict-luke object with entries dropped if the key name
            begin with a double underscore.
        
    """
    base = type(item)
    return base({k: v for k, v in item.items() if not k.startswith('__')})

@drop_dunders.register(MutableSequence)   
def drop_dunders_list(
    item: MutableSequence[str | object], /) -> MutableSequence[str | object]:
    """Drops items in 'item' beginning with a double underscore.

    Args:
        item (MutableSequence[str | object]): list-like object with str items or 
            names that might have double underscores at their beginnings.

    Returns:
        MutableSequence[str | object]: list-like object with items dropped if 
            they or their names begin with a double underscore.
            
    Raises:
        TypeError: if 'item' does not contain str types or objects with either
            'name' or '__name__' attributes.
        
    """
    base = type(item)
    if len(item) > 0 and all(isinstance(i, str) for i in item):
        return base([i for i in item if not i.startswith('__')])
    elif len(item) > 0 and all(hasattr(i, 'name') for i in item):
        return base([i for i in item if not i.name.startswith('__')])
    elif len(item) > 0 and all(hasattr(i, '__name__') for i in item):
        return base([i for i in item if not i.__name__.startswith('__')])
    elif len == 0:
        return item
    else:
        raise TypeError(
            'items in item must be str types or have name or __name__ '
            'attributes')
           
@functools.singledispatch
def drop_prefix(item: Any, /, prefix: str, divider: str = '') -> Any:
    """Drops 'prefix' from 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
            
    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_prefix.register
def drop_prefix_from_str(item: str, /, prefix: str, divider: str = '') -> str:
    """Drops 'prefix' from 'item' with 'divider' in between.
    
    Args:
        item (str): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
 
    Returns:
        str: modified str.

    """
    prefix = ''.join([prefix, divider])
    if item.startswith(prefix):
        return item[len(prefix):]
    else:
        return item

@drop_prefix.register(Mapping)
def drop_prefix_from_dict(
    item: Mapping[str, Any], /, 
    prefix: str, 
    divider: str = '') -> Mapping[str, Any]:
    """Drops 'prefix' from keys in 'item' with 'divider' in between.
    
    Args:
        item (Mapping[str, Any]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
 
    Returns:
        Mapping[str, Any]: modified mapping.

    """
    contents = {
        drop_prefix(item = k, prefix = prefix, divider = divider): v
        for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_prefix.register(MutableSequence)
def drop_prefix_from_list(
    item: MutableSequence[str], /, 
    prefix: str, 
    divider: str = '') -> MutableSequence[str]:
    """Drops 'prefix' from items in 'item' with 'divider' in between.
    
    Args:
        item (MutableSequence[str]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
 
    Returns:
        MutableSequence[str]: modified sequence.

    """
    contents = [
        drop_prefix(item = i, prefix = prefix, divider = divider) for i in item] 
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_prefix.register(Set)
def drop_prefix_from_set(
    item: Set[str], /, 
    prefix: str, 
    divider: str = '') -> Set[str]:
    """Drops 'prefix' from items in 'item' with 'divider' in between.
    
    Args:
        item (Set[str]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
 
    Returns:
        Set[str]: modified set.

    """
    contents = {
        drop_prefix(item = i, prefix = prefix, divider = divider) for i in item}   
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)  

@drop_prefix.register(tuple)
def drop_prefix_from_tuple(
    item: tuple[str, ...], /, 
    prefix: str, 
    divider: str = '') -> tuple[str, ...]:
    """Drops 'prefix' from items in 'item' with 'divider' in between.
    
    Args:
        item (tuple[str, ...]): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
 
    Returns:
        tuple[str, ...]: modified tuple.

    """
    return tuple(
        [drop_prefix(item = i, prefix = prefix, divider = divider) 
         for i in item])       
    
@functools.singledispatch
def drop_privates(item: Any, /) -> Any:
    """Drops items in 'item' with names beginning with an underscore.

    Args:
        item (Any): item to modify.

    Returns:
        Any: item with entries dropped beginning with an underscore.
        
    Raises:
        TypeError: if 'item' is not a registered type.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_privates.register(Mapping)
def drop_privates_dict(item: Mapping[str, Any], /) -> Mapping[str, Any]:
    """Drops items in 'item' with key names beginning with an underscore.

    Args:
        item (Mapping[str, Any]): dict-like object with str keys that might have
            underscores at the beginning of the key names.

    Returns:
        Mapping[str, Any]: dict-luke object with entries dropped if the key name
            begin with an underscore.
        
    """
    base = type(item)
    return base({k: v for k, v in item.items() if not k.startswith('_')})

@drop_privates.register(MutableSequence)   
def drop_privates_list(
    item: MutableSequence[str | object], /) -> MutableSequence[str | object]:
    """Drops items in 'item' with names beginning with an underscore.

    Args:
        item (MutableSequence[str | object]): list-like object with str items or 
            names that might have underscores at their beginnings.

    Returns:
        MutableSequence[str | object]: list-like object with items dropped if 
            they or their names begin with an underscore.
            
    Raises:
        TypeError: if 'item' does not contain str types or objects with either
            'name' or '__name__' attributes.
        
    """
    base = type(item)
    if len(item) > 0 and all(isinstance(i, str) for i in item):
        return base([i for i in item if not i.startswith('_')])
    elif len(item) > 0 and all(hasattr(i, 'name') for i in item):
        return base([i for i in item if not i.name.startswith('_')])
    elif len(item) > 0 and all(hasattr(i, '__name__') for i in item):
        return base([i for i in item if not i.__name__.startswith('_')])
    elif len == 0:
        return item
    else:
        raise TypeError(
            'items in item must be str types or have name or __name__ '
            'attributes')
                   
@functools.singledispatch
def drop_substring(item: Any, /, substring: str) -> Any:
    """Drops 'substring' from 'item' with a possible 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        substring (str): substring to be added to 'item'.
            
    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_substring.register
def drop_substring_from_str(item: str, /, substring: str) -> str:
    """Drops 'substring' from 'item'.
    
    Args:
        item (str): item to be modified.
        substring (str): substring to be added to 'item'.

    Returns:
        str: modified str.

    """
    if substring in item:
        return item.replace(substring, '')
    else:
        return item

@drop_substring.register(Mapping)
def drop_substring_from_dict(
    item: Mapping[str, Any], /, 
    substring: str) -> Mapping[str, Any]:
    """Drops 'substring' from keys in 'item'.
    
    Args:
        item (Mapping[str, Any]): item to be modified.
        substring (str): substring to be added to 'item'.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    contents = {
        drop_substring(item = k, substring = substring): v
        for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_substring.register(MutableSequence)
def drop_substring_from_list(
    item: MutableSequence[str], /, 
    substring: str) -> MutableSequence[str]:
    """Drops 'substring' from items in 'item'.
    
    Args:
        item (MutableSequence[str]): item to be modified.
        substring (str): substring to be added to 'item'.

    Returns:
        MutableSequence[str]: modified sequence.

    """
    contents = [drop_substring(item = i, substring = substring) for i in item] 
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_substring.register(Set)
def drop_substring_from_set(item: Set[str], /, substring: str) -> Set[str]:
    """Drops 'substring' from items in 'item'.
    
    Args:
        item (Set[str]): item to be modified.
        substring (str): substring to be added to 'item'.

    Returns:
        Set[str]: modified set.

    """
    contents = {drop_substring(item = i, substring = substring) for i in item}   
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)  

@drop_substring.register(tuple)
def drop_substring_from_tuple(
    item: tuple[str, ...], /, 
    substring: str) -> tuple[str, ...]:
    """Drops 'substring' from items in 'item'.
    
    Args:
        item (tuple[str, ...]): item to be modified.
        substring (str): substring to be added to 'item'.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return tuple(
        [drop_substring(item = i, substring = substring) for i in item])    
     
@functools.singledispatch
def drop_suffix(item: Any, /, suffix: str, divider: str = '') -> Any:
    """Drops 'suffix' from 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_suffix.register
def drop_suffix_from_str(item: str, /, suffix: str, divider: str = '') -> str:
    """Drops 'suffix' from 'item' with 'divider' in between.
    
    Args:
        item (str): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Returns:
        str: modified str.

    """
    suffix = ''.join([suffix, divider])
    if item.endswith(suffix):
        return item.removesuffix(suffix)
    else:
        return item

@drop_suffix.register(Mapping)
def drop_suffix_from_dict(
    item: Mapping[str, Any], /, 
    suffix: str, 
    divider: str = '') -> Mapping[str, Any]:
    """Drops 'suffix' from keys in 'item' with 'divider' in between.
    
    Args:
        item (Mapping[str, Any]): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Returns:
        Mapping[str, Any]: modified mapping.

    """
    contents = {
        drop_suffix(item = k, suffix = suffix, divider = divider): v 
        for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_suffix.register(MutableSequence)
def drop_suffix_from_list(
    item: MutableSequence[str], /, 
    suffix: str, 
    divider: str = '') -> MutableSequence[str]:
    """Drops 'suffix' from items in 'item' with 'divider' in between.
    
    Args:
        item (MutableSequence[str]): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Returns:
        MutableSequence[str]: modified sequence.

    """
    contents = [
        drop_suffix(item = i, suffix = suffix, divider = divider) for i in item]
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_suffix.register(Set)
def drop_suffix_from_set(
    item: Set[str], /, 
    suffix: str, 
    divider: str = '') -> Set[str]:
    """Drops 'suffix' from items in 'item' with 'divider' in between.
    
    Args:
        item (Set[str]): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Returns:
        Set[str]: modified set.

    """
    contents = {
        drop_suffix(item = i, suffix = suffix, divider = divider) for i in item}      
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)  

@drop_suffix.register(tuple)
def drop_suffix_from_tuple(
    item: tuple[str, ...], /, 
    suffix: str, 
    divider: str = '') -> tuple[str, ...]:
    """Drops 'suffix' from items in 'item' with 'divider' in between.
    
    Args:
        item (tuple[str, ...]): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Returns:
        tuple[str, ...]: modified tuple.

    """
    return tuple(
        [drop_suffix(item = i, suffix = suffix, divider = divider) 
         for i in item])        

""" Other Modifiers """

def capitalify(item: str) -> str:
    """Converts a snake case str to capital case.

    Args:
        item (str): str to convert.

    Returns:
        str: 'item' converted to capital case.

    """
    return item.replace('_', ' ').title().replace(' ', '')

def snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): str to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()

def uniquify(
    key: str, 
    dictionary: Mapping[Hashable, Any],
    index: Optional[int] = 1) -> str:
    """Creates a unique key name to avoid overwriting an item in 'dictionary'.
    
    The function is 1-indexed so that the first attempt to avoid a duplicate
    will be: "old_name2".

    Args:
        key (str): name of key to test.
        dictionary (Mapping[Hashable, Any]): dict for which a unique key name
            is sought.

    Returns:
        str: unique key name for 'dictionary'.
        
    """
    if key not in dictionary:
        return key
    else:
        counter = index
        while True:
            counter += 1
            if counter > 2:
                name = name.removesuffix(str(counter - 1))
            name = ''.join([key, str(counter)])
            if name not in dictionary:
                return name 
            