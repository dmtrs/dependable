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

    class B:
        def __init__(self, *, f: F = Depends(F)) -> None:
            self.f = f

    @dependant
    async def f(*, f: F = Depends(F), b: B = Depends(B)) -> Tuple[F, B]:
        return (f, b)

    f, b = await f()
    assert f is not b.f


@pytest.mark.asyncio
async def test_shortcut_syntax() -> None:
    import uuid

    class F:
        def __init__(self) -> None:
            self._id = uuid.uuid4()

    @dependant
    async def f(*, f: F = Depends()) -> F:
        return f

    actual = await f()
    assert isinstance(actual._id, uuid.UUID)


@pytest.mark.asyncio
async def test_instance() -> None:
    import uuid

    class F:
        async def __call__(self) -> uuid.UUID:
            return uuid.uuid4()

    @dependant
    async def f(*, f: uuid.UUID = Depends(F())) -> uuid.UUID:
        return f

    assert await f() is not await f()
