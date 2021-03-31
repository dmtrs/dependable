from typing import Any, Callable, List, Optional, TypeVar

T = TypeVar("T")


class Depends:
    def __init__(
        self, dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = False
    ):
        self.dependency = dependency
        self.use_cache = use_cache

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        cache = f", use_cache={self.use_cache}"
        return f"{self.__class__.__name__}({attr}{cache})"


class Dependant:
    def __init__(
        self,
        *,
        dependencies: Optional[List["Dependant"]] = None,
        name: Optional[str] = None,
        call: Callable[..., Any],
        # request_param_name: Optional[str] = None,
        # websocket_param_name: Optional[str] = None,
        # http_connection_param_name: Optional[str] = None,
        # response_param_name: Optional[str] = None,
        # background_tasks_param_name: Optional[str] = None,
        use_cache: bool = True,
        # path: Optional[str] = None,
    ) -> None:
        self.dependencies = dependencies or []
        # self.websocket_param_name = websocket_param_name
        # self.http_connection_param_name = http_connection_param_name
        # self.response_param_name = response_param_name
        # self.background_tasks_param_name = background_tasks_param_name
        self.name = name
        self.call = call
        self.use_cache = use_cache
        # Store the path to be able to re-generate a dependable from it in overrides
        # self.path = path
        self.cache_key = (self.call,)
