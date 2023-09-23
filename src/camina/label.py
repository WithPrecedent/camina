"""System and functions for inferring object and class names

Contents:


To Do:


"""
from __future__ import annotations
from collections.abc import Callable
import dataclasses
import inspect
from typing import Any, Optional, Type

from . import modify


def namify(item: Any, /, default: Optional[str] = None) -> Optional[str]:
    """Returns str name representation of 'item'.
    
    Args:
        item (Any): item to determine a str name.
        default(Optional[str]): default name to return if other methods at name
            creation fail.

    Returns:
        str: a name representation of 'item.'
        
    """        
    if isinstance(item, str):
        return item
    elif (
        hasattr(item, 'name') 
        and not inspect.isclass(item)
        and isinstance(item.name, str)):
        return item.name
    else:
        try:
            return modify.snakify(item.__name__)
        except AttributeError:
            if item.__class__.__name__ is not None:
                return modify.snakify(item.__class__.__name__) 
            else:
                return default


@dataclasses.dataclass
class Name(object):
    """Descriptor for a name attribute.
    
    This class automatically provides a name attribute to an object using the
    '_KEY_NAMER' function. 

    Args:
        _KEY_NAMER (Optional[Callable[[object | Type[Any]], str]]): function that
            creates a name if one has not been stored. Defaults to namify.
            
    Attributes:
        private_name (str): the name of the attribute in the owner instance 
            with a leading underscore added.
            
    """
    _KEY_NAMER: Optional[Callable[[object | Type[Any]], str]] = namify
        
    """ Dunder Methods """

    def __get__(
        self, 
        owner: object, 
        objtype: Optional[Type[Any]] = None) -> Any:
        """Returns name stored in 'private_name' of 'owner' of calls '_KEY_NAMER'.

        Args:
            owner (object): object of which this descriptor is an attribute.
            objtype (Optional[Type[Any]]): class of 'owner'. Defaults to None.

        Returns:
            Any: stored item.
            
        """
        try:
            return getattr(owner, self.private_name)
        except AttributeError:
            return self._KEY_NAMER(owner)            

    def __set__(self, owner: object, value: Any) -> None:
        """Stores 'value' in 'private_name' of 'owner'.

        Args:
            owner (object): object of which this descriptor is an attribute.
            value (Any): name to store.
            
        """
        setattr(owner, self.private_name, value)
        return    
    
    def __set_name__(self, owner: object, name: str) -> None:
        """Stores 'private_name' based on the attribute name in 'owner'.

        Args:
            owner (object): object of which this descriptor is an attribute.
            name (str): name of this attribute in 'owner'. 
            
        """
        self.private_name = f'_{name}'
        return
   