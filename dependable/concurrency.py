import asyncio
import functools
from typing import Any, Callable, Dict, TypeVar

T = TypeVar("T")

from .core import Dependant

asynccontextmanager_error_message = """
dependencies with yield require Python 3.7 or above,
or the backports for Python 3.6, installed with:
    pip install async-exit-stack async-generator
"""

try:
    from contextlib import asynccontextmanager as asynccontextmanager  # type: ignore
except ImportError:  # pragma: no cover
    try:
        from async_generator import (  # type: ignore  # isort: skip
            asynccontextmanager as asynccontextmanager,
        )
    except ImportError:  # pragma: no cover
        asynccontextmanager = None  # type: ignore


try:
    from contextlib import AsyncExitStack as AsyncExitStack  # type: ignore
except ImportError:  # pragma: no cover
    try:
        from async_exit_stack import AsyncExitStack as AsyncExitStack  # type: ignore
    except ImportError:  # pragma: no cover
        AsyncExitStack = None  # type: ignore


def check_dependency_contextmanagers() -> None:
    if AsyncExitStack is None or asynccontextmanager is None:  # pragma: no cover
        raise RuntimeError(asynccontextmanager_error_message)


# starlette/concurrency.py

try:
    import contextvars  # Python 3.7+ only or via contextvars backport.
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore


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
