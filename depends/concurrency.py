from typing import Any, AsyncGenerator, Callable, Dict, Iterator, TypeVar

from .core import Dependant

asynccontextmanager_error_message = """
dependencies with yield require Python 3.7 or above,
or the backports for Python 3.6, installed with:
    pip install async-exit-stack async-generator
"""


def _fake_asynccontextmanager(func: Callable[..., Any]) -> Callable[..., Any]:
    def raiser(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(asynccontextmanager_error_message)

    return raiser


try:
    from contextlib import asynccontextmanager as asynccontextmanager  # type: ignore
except ImportError:
    try:
        from async_generator import (  # type: ignore  # isort: skip
            asynccontextmanager as asynccontextmanager,
        )
    except ImportError:  # pragma: no cover
        asynccontextmanager = _fake_asynccontextmanager


try:
    from contextlib import AsyncExitStack as AsyncExitStack  # type: ignore
except ImportError:
    try:
        from async_exit_stack import AsyncExitStack as AsyncExitStack  # type: ignore
    except ImportError:  # pragma: no cover
        AsyncExitStack = None  # type: ignore


def check_dependency_contextmanagers() -> None:
    if AsyncExitStack is None or asynccontextmanager == _fake_asynccontextmanager:
        raise RuntimeError(asynccontextmanager_error_message)  # pragma: no cover


# starlette/concurrency.py

import asyncio
import functools
import sys

try:
    import contextvars  # Python 3.7+ only or via contextvars backport.
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore

if sys.version_info >= (3, 7):  # pragma: no cover
    pass
else:  # pragma: no cover
    pass

T = TypeVar("T")

"""
async def run_until_first_complete(*args: Tuple[Callable[..., Any], Dict[Any]]) -> None:
    tasks = [create_task(handler(**kwargs)) for handler, kwargs in args]
    (done, pending) = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    [task.cancel() for task in pending]
    [task.result() for task in done]
"""


async def run_in_threadpool(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    loop = asyncio.get_event_loop()
    if contextvars is not None:  # pragma: no cover
        # Ensure we run in the same context
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:  # pragma: no cover
        # loop.run_in_executor doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)


class _StopIteration(Exception):
    pass


def _next(iterator: Iterator[T]) -> Any:
    # We can't raise `StopIteration` from within the threadpool iterator
    # and catch it outside that context, so we coerce them into a different
    # exception type.
    try:
        return next(iterator)
    except StopIteration:
        raise _StopIteration


async def iterate_in_threadpool(iterator: Iterator[T]) -> AsyncGenerator[T, None]:
    while True:
        try:
            yield await run_in_threadpool(_next, iterator)
        except _StopIteration:
            break


async def run_function(
    *, dependant: Dependant, values: Dict[str, Any], is_coroutine: bool
) -> Any:
    # Only called by get_request_handler. Has been split into its own function to
    # facilitate profiling endpoints, since inner functions are harder to profile.
    assert dependant.call is not None, "dependant.call must be a function"

    if is_coroutine:
        return await dependant.call(**values)
    else:
        return await run_in_threadpool(dependant.call, **values)
