from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Generator,
    Iterator,
    List,
    TypeVar,
)

import pytest

from dependable import Depends, dependant

T = TypeVar("T")


class TestDependant:
    def test_assertion(self) -> None:
        try:
            dependant(1)  # type: ignore
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        @dependant
        def empty() -> Any:
            return True

        assert await empty()

    @pytest.mark.asyncio
    async def test_arg(self) -> None:
        @dependant
        def _is(*, b: bool) -> bool:
            return b

        assert await _is(b=True)

    @pytest.mark.asyncio
    async def test_depends(self) -> None:
        def falsy() -> bool:
            return False

        @dependant
        def _is(*, actual: bool = Depends(falsy)) -> bool:
            return actual

        assert await _is(actual=True)
        assert not await _is(actual=False)
        assert not await _is()

    @pytest.mark.asyncio
    async def test_generator(self) -> None:
        expected = ["hello", "world"]

        def gen() -> Generator[str, None, None]:
            for f in expected:
                yield f

        @dependant
        async def collect(words: Iterator[str] = Depends(gen)) -> List[str]:
            actual = []
            for w in words:
                actual.append(w)
            return actual

        assert expected == await collect()

    @pytest.mark.asyncio
    async def test_async_generator(self) -> None:
        expected = ["hello", "world"]

        async def gen() -> AsyncGenerator[str, None]:
            for f in expected:
                yield f

        @dependant
        async def collect(words: AsyncIterator[str] = Depends(gen)) -> List[str]:
            actual = []
            async for w in words:
                actual.append(w)
            return actual

        assert expected == await collect()
