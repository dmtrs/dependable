from dataclasses import dataclass
from typing import AsyncGenerator, AsyncIterator, Generator, Iterator, List, TypeVar

import pytest

from dependable import Depends, dependant

T = TypeVar("T")

dot = lambda: "."


def char(c: str = Depends(dot)) -> str:
    return c


class TestDecoratorDependant:
    @pytest.mark.asyncio
    async def test_in_threadpool(self) -> None:
        dot = dependant(char)
        assert await dot() == "."

    @pytest.mark.asyncio
    async def test_coroutine(self) -> None:
        async def async_char(c: str = Depends(char)) -> str:
            return c

        dot = dependant(async_char)
        assert await dot() == "."

    @pytest.mark.asyncio
    async def test_str_annotation(self) -> None:
        @dataclass
        class C:
            value = "."

        async def async_char(c: C = Depends()) -> str:
            return c.value

        dot = dependant(async_char)
        assert await dot() == "."

    @pytest.mark.asyncio
    async def test_override(self) -> None:
        overrides = {dot: lambda: "x"}
        dash = dependant(char, overrides=overrides)

        assert await dash() == "x"

    @pytest.mark.asyncio
    async def test_ok(self) -> None:
        async def async_char(c: str = Depends(char)) -> str:
            raise Exception

        dot = dependant(async_char)

        with pytest.raises(Exception):
            assert await dot() == "."

    @pytest.mark.asyncio
    async def test_use_cache(self) -> None:
        # arrange
        from random import random as _rndm
        def _random() -> float:
            return _rndm()

        random = dependant(_random)

        # act / assert
        assert await random() is not await random()

        # arrange
        def single_cached(r: float = Depends(_random, use_cache=True)) -> float:
            return r

        still_random = dependant(single_cached)

        # act / assert
        assert await still_random() is not await still_random()

        # arrange

        @dependant
        def cached(
            r: float = Depends(_random), x: float = Depends(_random, use_cache=True)
        ) -> float:
            return r is x

        # act / assert
        assert await cached()

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

    @pytest.mark.asyncio
    async def test_callable_class(self) -> None:
        class C:
            async def __call__(self) -> float:
                return 1.0

        async def foo(c: float = Depends(C())) -> float:
            return c

        awaitable_foo = dependant(foo)
        assert await awaitable_foo() == 1.0
