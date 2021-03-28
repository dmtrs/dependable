from typing import Any, Callable, TypeVar

from .utils import get_dependant, solve_dependencies

T = TypeVar("T")


class dependable:
    def __init__(self, call: Callable[..., T]) -> None:
        assert callable(call)
        self.call = call
        self.dependant = get_dependant(call=call)

    async def __call__(self, *args: Any, **kwargs: Any) -> T:
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
        results = await solve_dependencies(dependant=self.dependant)
        return self.call(*args, **kwargs)
