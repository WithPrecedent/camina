"""Functions for changing camina settings

Contents:

To Do:


"""
from __future__ import annotations
from collections.abc import Callable
from typing import Any, Type

from . import configuration
    

def set_key_namer(namer: Callable[[object | Type[Any]], str]) -> None:
    """Sets the global default function used to name items.

    Args:
        namer (Callable[[object | Type[Any]], str]): function that returns a 
            str name of any item passed.

    Raises:
        TypeError: if 'namer' is not callable.
        
    """
    if isinstance(namer, Callable):
        configuration.KEYER = namer
    else:
        raise TypeError('namer argument must be a callable')

def set_method_namer(namer: Callable[[object | Type[Any]], str]) -> None:
    """Sets the global default function used to name factory methods.

    Args:
        namer (Callable[[object | Type[Any]], str]): function that returns a 
            str name of any item passed.

    Raises:
        TypeError: if 'namer' is not callable.
        
    """
    if isinstance(namer, Callable):
        configuration.METHOD_NAMER = namer
    else:
        raise TypeError('namer argument must be a callable')
    