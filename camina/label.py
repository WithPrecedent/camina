"""
label: system and functions for inferring object and class names
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
    capitalify: converts a snake case str to capital case.
    snakify: converts a capital case str to snake case.
    uniquify: returns a unique key for a dict.

ToDo:
    Reintegrate dispatcher from ashworth package once it has been tested.

"""
from __future__ import annotations

from collections.abc import Hashable, Mapping, MutableSequence, Sequence, Set
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
    