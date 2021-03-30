import asyncio
import pytest
from typing import Dict, Tuple
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


@pytest.mark.asyncio
async def test_boilerplate() -> None:
    import uuid
    import time
    
    async def some_service() -> uuid.UUID:
        await asyncio.sleep(1)
        return uuid.uuid4()

    async def  main() -> Tuple[uuid.UUID, uuid.UUID]:
        _id: uuid.UUID = await some_service()
        other_id: uuid.UUID = await some_service()
        return (_id, other_id)

    @dependant
    async def main_with_depends(
        *, _id: uuid.UUID = Depends(some_service), other_id: uuid.UUID = Depends(some_service),
    ) -> Tuple[uuid.UUID, uuid.UUID]:
        return (_id, other_id)

    pt = time.process_time()
    t = time.time()
    await main()
    elapsed_pt = (time.process_time() - pt)
    elapsed_t = (time.time() - t)
    print(f'process: {elapsed_pt}, time: {elapsed_t}')

    pt = time.process_time()
    t = time.time()
    await main_with_depends()
    elapsed_pt = (time.process_time() - pt)
    elapsed_t = (time.time() - t)
    print(f'process: {elapsed_pt}, time: {elapsed_t}')
