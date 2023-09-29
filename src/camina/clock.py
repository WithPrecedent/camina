"""Date and time related tools

Contents:
    how_soon_is_now: returns current date and time as a str.
    timer: computes the time it takes for the wrapped `process` to complete.

To Do:
    Add mechanisms for `timer` to record results in logger and/or the python
        terminal.

"""
from __future__ import annotations

import datetime
import time
from typing import TYPE_CHECKING, Any

from . import convert

if TYPE_CHECKING:
    from collections.abc import Callable


def how_soon_is_now(
    prefix: str | None = None,
    time_format: str | None = '%Y-%m-%d_%H-%M') -> str:
    """Creates a string from current date and time.

    Args:
        prefix: a prefix to add to the returned str.
        time_format: format to create a str from datetime. The passed argument
            should follow the rules of datetime.strftime. Defaults to
            '%Y-%m-%d_%H-%M'.

    Returns:
        str: with current date and time in `time_format` format.

    """
    time_string = convert.datetime_to_string(
        item = datetime.datetime.now(tz_info = datetime.timezone.utc),
        time_format = time_format)
    if prefix is not None:
        return f'{prefix}{time_string}'
    else:
        return time_string

def timer(
    process: Callable[..., Any | None]) -> (Callable[..., Any | None]):
    """Decorator for computing the length of time a process takes.

    Args:
        process: wrapped callable to compute the time it takes to complete its
            execution.

    """
    try:
        name = process.__name__
    except AttributeError:
        name = process.__class__.__name__
    def shell_timer(operation: Callable[..., Any | None]) -> (
        Callable[..., Any | None]):
        def decorated(*args: Any, **kwargs: Any) -> (
            Callable[..., Any | None]):
            def convert_time(seconds: int | float) -> tuple[int, int, int]:
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                return int(hours), int(minutes), int(seconds)
            implement_time = time.time()
            result = operation(*args, **kwargs)
            total_time = time.time() - implement_time
            h, m, s = convert_time(total_time)
            print(f'{name} completed in %d:%02d:%02d' % (h, m, s))
            return result
        return decorated
    return shell_timer
