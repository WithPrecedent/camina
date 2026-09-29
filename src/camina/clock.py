"""Date and time related tools.

Contents:
    how_soon_is_now: returns current date and time as a str.
    timer: computes the time it takes for the wrapped `process` to complete.

To Do:
    Add mechanisms for `timer` to record results in logger and/or the python
        terminal.

"""

from __future__ import annotations

import datetime
import functools
import time
from typing import TYPE_CHECKING, Any

from . import convert

if TYPE_CHECKING:
    from collections.abc import Callable


def how_soon_is_now(
    prefix: str | None = None, time_format: str | None = "%Y-%m-%d_%H-%M"
) -> str:
    """Creates a string from current date and time.

    Args:
        prefix (str | None): a prefix to add to the returned str. Defaults to
            None.
        time_format (str | None): format to create a str from datetime. The
            passed argument should follow the rules of datetime.strftime.
            Defaults to "%Y-%m-%d_%H-%M".

    Returns:
        str: with current date and time (in the local timezone) in
            `time_format` format.

    """
    time_string = convert.datetime_to_str(
        datetime.datetime.now().astimezone(), time_format=time_format
    )
    if prefix is not None:
        return f"{prefix}{time_string}"
    return time_string


def timer(process: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for computing the length of time a process takes.

    When the decorated callable finishes, a message of the form
    "name completed in H:MM:SS" is printed. The wrapped callable's return value
    is passed through unchanged.

    Args:
        process (Callable[..., Any]): wrapped callable to compute the time it
            takes to complete its execution.

    Returns:
        Callable[..., Any]: decorated version of `process`.

    """
    name = getattr(process, "__name__", type(process).__name__)

    @functools.wraps(process)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = process(*args, **kwargs)
        minutes, seconds = divmod(int(time.perf_counter() - start), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"{name} completed in {hours}:{minutes:02d}:{seconds:02d}")  # noqa: T201
        return result

    return decorated
