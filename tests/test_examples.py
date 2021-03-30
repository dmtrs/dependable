import asyncio
import pytest
from typing import Dict
from collections import defaultdict

from dependable import dependant, Depends

@pytest.mark.asyncio
async def test_gotcha() -> None:
    async def foo(r: Dict[str, str] = {} ) -> Dict[str, str]:
        return r

    assert await foo() is await foo() is not {}

    @dependant
    async def bar(r: Dict[str, str] = Depends(lambda: {})) -> Dict[str, str]:
        return r

    assert await bar() is not await bar() is not {}


@pytest.mark.asyncio
async def test_awaitable() -> None:
    async def f() -> Dict[str, str]:
        return {}

    async def foo(r: Dict[str, str] = await f()) -> Dict[str, str]:
        return r

    assert await foo() is await foo() is not await f()

    @dependant
    async def bar(r: Dict[str, str] = Depends(f)) -> Dict[str, str]:
        return r

    assert await bar() is not await bar() is not await f()

    
