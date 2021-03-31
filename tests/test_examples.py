from typing import Dict, Tuple

import pytest

from dependable import Depends, dependant


@pytest.mark.asyncio
async def test_gotcha() -> None:
    async def foo(r: Dict[str, str] = {}) -> Dict[str, str]:
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

    async def some_service() -> uuid.UUID:
        return uuid.uuid4()

    @dependant
    async def combine(
        *,
        _id: uuid.UUID = Depends(some_service),
        other_id: uuid.UUID = Depends(some_service, use_cache=True),
        oid: uuid.UUID = Depends(some_service),
    ) -> Tuple[uuid.UUID, uuid.UUID, uuid.UUID]:
        return (_id, other_id, oid)

    _id, other_id, oid = await combine()
    assert _id is other_id is not oid


@pytest.mark.asyncio
async def test_class() -> None:
    class F:
        def __init__(self) -> None:
            pass

    @dependant
    async def f(*, f: F = Depends(F)) -> F:
        return f

    assert await f() is not await f()
