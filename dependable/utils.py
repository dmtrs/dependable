import inspect
from typing import Any, Callable, Dict, List, MutableMapping, Optional, Tuple

from .concurrency import check_dependency_contextmanagers, run_in_threadpool
from .core import Dependant, Depends

Scope = MutableMapping[str, Any]


def is_coroutine_callable(call: Callable[..., Any]) -> bool:
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    call = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(call)


def is_async_gen_callable(call: Callable[..., Any]) -> bool:
    if inspect.isasyncgenfunction(call):
        return True
    call = getattr(call, "__call__", None)
    return inspect.isasyncgenfunction(call)


def is_gen_callable(call: Callable[..., Any]) -> bool:
    if inspect.isgeneratorfunction(call):
        return True
    call = getattr(call, "__call__", None)
    return inspect.isgeneratorfunction(call)


"""
async def solve_generator(
    *, call: Callable[..., Any], stack: AsyncExitStack, sub_values: Dict[str, Any]
) -> Any:
    if is_gen_callable(call):
        cm = contextmanager_in_threadpool(contextmanager(call)(**sub_values))
    elif is_async_gen_callable(call):
        if not inspect.isasyncgenfunction(call):
            # asynccontextmanager from the async_generator backfill pre python3.7
            # does not support callables that are not functions or methods.
            # See https://github.com/python-trio/async_generator/issues/32
            #
            # Expand the callable class into its __call__ method before decorating it.
            # This approach will work on newer python versions as well.
            call = getattr(call, "__call__", None)
        cm = asynccontextmanager(call)(**sub_values)
    return await stack.enter_async_context(cm)
"""


def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    signature = inspect.signature(call)
    getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=param.annotation,
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_param_sub_dependant(
    *,
    param: inspect.Parameter,
) -> Dependant:
    depends: Depends = param.default
    if depends.dependency:
        dependency = depends.dependency
    else:
        dependency = param.annotation
    return get_dependant(
        call=dependency,
        name=param.name,
        use_cache=depends.use_cache,
    )


def get_dependant(
    *,
    call: Callable[..., Any],
    name: Optional[str] = None,
    use_cache: bool = True,
) -> Dependant:
    call_signature = get_typed_signature(call)
    signature_params = call_signature.parameters
    if is_gen_callable(call) or is_async_gen_callable(call):
        check_dependency_contextmanagers()
    dependant = Dependant(call=call, name=name, use_cache=use_cache)
    for param_name, param in signature_params.items():
        if isinstance(param.default, Depends):
            sub_dependant = get_param_sub_dependant(param=param)
            dependant.dependencies.append(sub_dependant)
            continue

    return dependant


async def solve_dependencies(
    *,
    dependant: Dependant,
    dependency_overrides_provider: Optional[Any] = None,
    dependency_cache: Optional[
        Dict[
            Tuple[
                Callable[..., Any],
            ],
            Any,
        ]
    ] = None,
    scope: Optional[Scope] = None,
) -> Tuple[Dict[str, Any], List[Exception], Dict[Tuple[Callable[..., Any],], Any,],]:
    values: Dict[str, Any] = {}
    errors: List[Exception] = []
    dependency_cache = dependency_cache or {}
    sub_dependant: Dependant

    for sub_dependant in dependant.dependencies:
        # sub_dependant.call = cast(Callable[..., Any], sub_dependant.call)
        # sub_dependant.cache_key = cast(
        #     Tuple[Callable[..., Any]], sub_dependant.cache_key
        # )
        call = sub_dependant.call
        use_sub_dependant = sub_dependant
        if (
            dependency_overrides_provider
            and dependency_overrides_provider.dependency_overrides
        ):
            original_call = sub_dependant.call
            call = getattr(
                dependency_overrides_provider, "dependency_overrides", {}
            ).get(original_call, original_call)
            use_sub_dependant = get_dependant(
                call=call,
                name=sub_dependant.name,
            )

        solved_result = await solve_dependencies(
            dependant=use_sub_dependant,
            dependency_overrides_provider=dependency_overrides_provider,
            dependency_cache=dependency_cache,
        )
        (
            sub_values,
            sub_errors,
            sub_dependency_cache,
        ) = solved_result
        dependency_cache.update(sub_dependency_cache)
        if sub_errors:
            errors.extend(sub_errors)
            continue
        if sub_dependant.use_cache and sub_dependant.cache_key in dependency_cache:
            solved = dependency_cache[sub_dependant.cache_key]

        elif is_coroutine_callable(call):
            solved = await call(**sub_values)
        else:
            solved = await run_in_threadpool(call, **sub_values)
        if sub_dependant.name is not None:
            values[sub_dependant.name] = solved
        if sub_dependant.cache_key not in dependency_cache:
            dependency_cache[sub_dependant.cache_key] = solved
        """
        # generator support
        elif is_gen_callable(call) or is_async_gen_callable(call):
            stack = scope.get("fastapi_astack") if scope else None
            if stack is None:
                raise RuntimeError(
                    asynccontextmanager_error_message
                )  # pragma: no cover
            solved = await solve_generator(
                call=call, stack=stack, sub_values=sub_values
            )
        """

    return values, errors, dependency_cache
