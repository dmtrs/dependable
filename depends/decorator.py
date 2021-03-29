import asyncio
from typing import Any, Callable, TypeVar

from .concurrency import run_function
from .core import Dependant
from .utils import get_dependant, solve_dependencies

T = TypeVar("T")


class dependable:
    def __init__(self, call: Callable[..., Any]) -> None:
        assert callable(call)
        self.call = call
        self.dependant: Dependant = get_dependant(call=call)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        is_coroutine: bool = asyncio.iscoroutinefunction(self.dependant.call)
        """
        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if self.root_path:
                scope["root_path"] = self.root_path
            if AsyncExitStack:
                async with AsyncExitStack() as stack:
                    scope["fastapi_astack"] = stack
                    await super().__call__(scope, receive, send)
            else:
                await super().__call__(scope, receive, send)  # pragma: no cover
        """
        values, errors, dependency_cache = await solve_dependencies(
            dependant=self.dependant
        )
        values.update(kwargs)
        return await run_function(
            dependant=self.dependant, values=values, is_coroutine=is_coroutine
        )
        # self.call(*args, **kwargs)
