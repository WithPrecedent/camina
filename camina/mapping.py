"""
mapping: extensible, flexible, lightweight dict-like classes
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
    Dictionary (bunches.Bunch, MutableMapping): drop-in replacement 
        for a python dict with some added functionality.
    Catalog (Dictionary): wildcard-accepting dict which is primarily intended 
        for storing different options and strategies. It also returns lists of 
        matches if a list of keys is provided.
    Repository (Dictionary): stores items using inferred keys when the 'add'
        method is called.
        
ToDo:

       
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import copy
import dataclasses
from typing import Any, Optional

from . import base
from . import convert
from . import label
from . import rules
from . import modify
                  

@dataclasses.dataclass 
class Dictionary(base.Bunch, MutableMapping): 
    """Basic camina dict replacement.
    
    A Dictionary differs from an ordinary python dict in ways inherited from 
    Bunch by requiring 'add' and 'subset' methods, storing data in 'contents', 
    and allowing the '+' operator to join Dictionary instances with other 
    mappings, including Dictionary instances. 
    
    In addition, it differs in 2 other significant ways:
        1) When returning 'keys', 'values' and 'items', this class returns them
            as tuples instead of KeysView, ValuesView, and ItemsView.
        2) It includes the same functionality as 'defaultdict' in the python 
            standard library, including a 'setdefault' method.
    
    Args:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
                          
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None

    """ Class Methods """
    
    @classmethod
    def fromkeys(
        cls, 
        keys: Sequence[Hashable], 
        value: Any, 
        **kwargs: Any) -> Dictionary:
        """Emulates the 'fromkeys' class method from a python dict.

        Args:
            keys (Sequence[Hashable]): items to be keys in a new Dictionary.
            value (Any): the value to use for all values in a new Dictionary.

        Returns:
            Dictionary: formed from 'keys' and 'value'.
            
        """
        return cls(contents = dict.fromkeys(keys, value), **kwargs)     
     
    """ Instance Methods """
     
    def add(self, item: Mapping[Hashable, Any], **kwargs: Any) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Mapping[Hashable, Any]): items to add to 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.update(item, **kwargs)
        return

    def delete(self, item: Hashable) -> None:
        """Deletes 'item' in 'contents'.

        Args:
            item (Hashable): key in 'contents' to delete the key/value pair.

        """
        del self.contents[item]
        return

    def get(self, key: Hashable, default: Optional[Any] = None) -> Any:
        """Returns value in 'contents' or default options.
        
        Args:
            key (Hashable): key for value in 'contents'.
            default (Optional[Any]): default value to return if 'key' is not 
                found in 'contents'.
        
        Raises:
            KeyError: if 'key' is not in the Dictionary and 'default' and the
                'default_factory' attribute are both None.
        
        Returns:
            Any: value matching key in 'contents' or 'default_factory' value. 
            
        """
        try:
            return self[key]
        except (KeyError, TypeError):
            if default is None:
                if self.default_factory is None:
                    raise KeyError(f'{key} is not in the Dictionary')
                else:
                    try:
                        return self.default_factory()
                    except TypeError:
                        return self.default_factory
            else:
                return default
                
    def items(self) -> tuple[tuple[Hashable, Any], ...]:
        """Emulates python dict 'items' method.
        
        Returns:
            tuple[tuple[Hashable], Any]: a tuple equivalent to dict.items(). 
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> tuple[Hashable, ...]:
        """Returns 'contents' keys as a tuple.
        
        Returns:
            tuple[Hashable, ...]: a tuple equivalent to dict.keys().
            
        """
        return tuple(self.contents.keys())

    def setdefault(self, value: Any) -> None:
        """sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return when 'get' is called and the
                'default' parameter to 'get' is None.
            
        """
        self.default_factory = value 
        return
               
    def subset(
        self, 
        include: Optional[Hashable | Sequence[Hashable]] = None, 
        exclude: Optional[Hashable | Sequence[Hashable]] = None) -> Dictionary:
        """Returns a new instance with a subset of 'contents'.

        This method applies 'include' before 'exclude' if both are passed. If
        'include' is None, all existing items will be added to the new subset
        class instance before 'exclude' is applied.
        
        Args:
            include (Optional[Hashable | Sequence[Hashable]]): key(s) to 
                include in the new Dictionary instance.
            exclude (Optional[Hashable | Sequence[Hashable]]): key(s) to 
                exclude from the new Dictionary instance.                
        
        Raises:
            ValueError: if 'include' and 'exclude' are both None.
                  
        Returns:
            Dictionary: with only keys from 'include' and no keys in 'exclude'.

        """
        if include is None and exclude is None:
            raise ValueError('include or exclude must not be None')
        else:
            if include is None:
                contents = copy.deepcopy(self.contents)
            else:
                include = list(convert.iterify(include)) 
                contents = {k: self.contents[k] for k in include}
            if exclude is not None:
                exclude = list(convert.iterify(exclude))
                contents = {
                    k: v for k, v in contents.items() 
                    if k not in exclude}
            new_dictionary = copy.deepcopy(self)
            new_dictionary.contents = contents
        return new_dictionary
      
    def values(self) -> tuple[Any, ...]:
        """Returns 'contents' values as a tuple.
        
        Returns:
            tuple[Any, ...]: a tuple equivalent to dict.values().
            
        """
        return tuple(self.contents.values())

    """ Dunder Methods """

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            key (Hashable): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return
    

@dataclasses.dataclass 
class Catalog(Dictionary):
    """Wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Dictionary and an ordinary 
    python dict.

    A Catalog differs from a Dictionary in 5 significant ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'default' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'default' is not passed when the instance is initialized, the 
            initial value of 'default' is 'all'.
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching values 
            returned. For example, 'catalog[['first_key', 'second_key']]' will 
            return the values for those keys in a list ['first_value',
            'second_value'].
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single type will be returned.

    Args:
        contents (Mapping[Hashable, Any]]): stored dictionary. Defaults to an 
            empty dict.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
        default (Optional[Any]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False.
                     
    """
    contents: Mapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None
    default: Optional[Any] = 'all'
    always_return_list: bool = False

    """ Instance Methods """
    
    def delete(self, item: Hashable | Sequence[Hashable]) -> None:
        """Deletes 'item' in 'contents'.

        Args:
            item (Hashable | Sequence[Hashable]): name(s) of key(s) in 
                'contents' to delete the key/value pair.

        """
        keys = list(convert.iterify(item))
        if all(k in self for k in keys):
            self.contents = {
                i: self.contents[i] for i in self.contents if i not in keys}
        else:
            raise KeyError(f'{item} not found in the Catalog')
        return
    
    """ Dunder Methods """

    def __getitem__(
        self, 
        key: Hashable | Sequence[Hashable]) -> Any | Sequence[Any]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Hashable | Sequence[Hashable]): key(s) in 'contents'.

        Returns:
            Any | Sequence[Any]: value(s) stored in 'contents'.

        """
        # Returns a list of all values if the 'all' key is sought.
        if key in rules.ALL_KEYS:
            return list(self.contents.values())
        # Returns a list of values for keys listed in 'default' attribute.
        elif key in rules.DEFAULT_KEYS:
            return self[self.default]
        # Returns an empty list if a null value is sought.
        elif key in rules.NONE_KEYS:
            if self.default_factory is None:
                if self.always_return_list:
                    return []
                else:
                    return None
            else:
                try:
                    return self.default_factory()
                except TypeError:
                    return self.default_factory
        # Returns list of matching values if 'key' is list-like.        
        elif isinstance(key, Sequence) and not isinstance(key, str):
            return [self.contents[k] for k in key if k in self.contents]
        # Returns matching value if key is not a non-str Sequence or wildcard.
        else:
            try:
                if self.always_return_list:
                    return [self.contents[key]]
                else:
                    return self.contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(
        self, 
        key: Hashable | Sequence[Hashable], 
        value: Any | Sequence[Any]) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            key (Hashable | Sequence[Hashable]): key(s) to set in 'contents'.
            value (Any | Sequence[Any]): value(s) to be paired with 'key' in 
                'contents'.

        """
        try:
            self.contents[key] = value
        except TypeError:
            self.contents.update(dict(zip(key, value)))
        return


@dataclasses.dataclass 
class Repository(Dictionary):
    """Dictionary with inferred keys based on items added.
    
    A Repository differs from an ordinary python dict in ways inherited from 
    Dictionary. In addition, it differs in 2 other significant ways:
        1) The 'add' method relies on the internal '_get_name__' method to 
            assign a str key for the passed item.
        2) It includes an 'overwrite' parameter which allows users to determine
            whether existing items will be overwritten when the inferred key
            matches an existing one or whether a new key will be inferred by
            adding an integer counter as a suffix to the key.
    
    Args:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
        overwrite (Optional[bool]): whether to overwrite existing items in the
            stored dictionary with the same inferred keys (True) or 
            automatically infer a new key based upon a counter suffix (False).
            Defaults to False.
                          
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None
    overwrite: Optional[bool] = False
        
    """ Instance Methods """

    def add(self, item: Any, key: Optional[str] = None, **kwargs: Any) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Any): item to add to 'contents' attribute.
            key (Optional[str]): key to use for 'item' if the user does not want
                the key to be inferred.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        key = key or self._get_name(item = item)
        if not self.overwrite:
            key = modify.uniquify(key = key, dictionary = self)
        self.contents.update({key: item}, **kwargs)
        return
    
    """ Private Methods """
    
    def _get_name(self, item: Any) -> str:
        """Infers key name for 'item'

        By default, this method uses the 'namify' function in camina. Override
        this method to use a different naming function.
        
        Args:
            item (Any): item to infer the name for.

        Returns:
            str: inferred name.
            
        """
        return label.namify(item)
    