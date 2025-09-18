"""Utility functions for the Gitingest package."""

import asyncio
import functools
from typing import Awaitable, Callable, TypeVar

from gitingest.utils.compat_typing import ParamSpec
from gitingest.utils.exceptions import AsyncTimeoutError

T = TypeVar("T")
P = ParamSpec("P")


class async_timeout:  # pylint: disable=invalid-name
    """Async Timeout decorator.

    This decorator wraps an asynchronous function and ensures it does not run for
    longer than the specified number of seconds. If the function execution exceeds
    this limit, it raises an ``AsyncTimeoutError``.

    Parameters
    ----------
    seconds : int
        The maximum allowed time (in seconds) for the asynchronous function to complete.

    """

    def __init__(self, seconds: int):
        self.seconds = seconds

    def __call__(self, func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            timeout = kwargs.get("timeout", self.seconds)
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError as exc:
                msg = f"Operation timed out after {timeout} seconds"
                raise AsyncTimeoutError(msg) from exc

        return wrapper
