import asyncio
from typing import Any, Callable, Dict, Optional, TypeVar

from .concurrency import run_function
from .core import Dependant
from .utils import get_dependant, solve_dependencies

T = TypeVar("T")

Call = Callable[..., Any]


class dependant:
    call: Callable[..., Any]
    dependant: Dependant
    overrides: Optional[Dict[Call, Call]] = None

    def __new__(
        cls,
        call: Optional[Call],
        *,
        overrides: Optional[Dict[Call, Call]] = None,
    ) -> Any:
        assert callable(call)
        obj = super(dependant, cls).__new__(cls)
        obj.call = call
        obj.dependant = get_dependant(call=call)
        if overrides:
            obj.overrides = overrides
        return obj

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
            dependant=self.dependant,
            overrides=self.overrides,
            dependency_cache=None,
        )

        values.update(kwargs)
        return await run_function(
            dependant=self.dependant, values=values, is_coroutine=is_coroutine
        )
        # self.call(*args, **kwargs)
