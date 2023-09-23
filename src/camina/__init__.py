"""Flexible, lightweight, extensible, easy-to-use data structures and types"""

from __future__ import annotations

__version__ = '0.1.16'

__author__: str = 'Corey Rayburn Yung'

__all__: list[str] = []


from .base import Base, Descriptor, Proxy
from .clock import how_soon_is_now, timer
import configuration
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
from .label import *
from .mapping import *
from .modify import *
from .sequence import *