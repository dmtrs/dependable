import pytest

import asyncio
from typing import Callable, Any, Sequence

from depends.concurrency import run_in_threadpool



class BackgroundTask:
    def __init__(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_async = asyncio.iscoroutinefunction(func)

    async def __call__(self) -> None:
        if self.is_async:
            await self.func(*self.args, **self.kwargs)
        else:
            await run_in_threadpool(self.func, *self.args, **self.kwargs)


class BackgroundTasks(BackgroundTask):
    def __init__(self, tasks: Sequence[BackgroundTask] = []):
        self.tasks = list(tasks)

    def add_task(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        task = BackgroundTask(func, *args, **kwargs)
        self.tasks.append(task)

    async def __call__(self) -> None:
        for task in self.tasks:
            await task()

class TestBackgroundTask:
    @pytest.mark.asyncio
    async def test_ok(self) -> None:
        def foo() -> str:
            return 'foo'

        task = BackgroundTask(foo)
        await task()

