from collections.abc import Callable

from typing import TypeVar, Any, Tuple, Optional

T = TypeVar('T')

class dependable:
    def __init__(self, fn: Callable[..., T]) -> None:
        self._fn = fn

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        return self._fn(*args, **kwargs)

