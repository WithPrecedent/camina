"""Settings for `camina`

Contents:


To Do:


"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any

from . import convert

if TYPE_CHECKING:
    from collections.abc import Callable


ALL_KEYS: list[Any] = ['all', 'All', ['all'], ['All']]
DEFAULT_KEYS: list[Any] = [
    'default', 'defaults', 'Default', 'Defaults', ['default'], ['defaults'], 
    ['Default'], ['Defaults']]
KEY_NAMER: Callable[[object | type[Any]], str] = convert.namify
METHOD_NAMER: Callable[[object | type[Any]], str] = (
    lambda x: f'from_{convert.namify(x)}')
NONE_KEYS: list[Any] = ['none', 'None', ['none'], ['None']]


@dataclasses.dataclass
class MISSING_VALUE(object):
    """Sentinel object for a missing data or parameter.

    This follows the same pattern as the `_MISSING_TYPE` class in the builtin
    dataclasses library. 
    https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py#L182-L186

    Because None is sometimes a valid argument or data option, this class
    provides an alternative that does not create the confusion that a default of 
    None can sometimes lead to.

    """

    pass  # noqa: PIE790


# MISSING, instance of MISSING_VALUE, should be used for missing values as an 
# alternative to None. This provides a fuller repr and traceback.
MISSING = MISSING_VALUE()
