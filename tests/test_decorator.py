from typing import Any, TypeVar

import pytest

from depends import Depends, dependable

T = TypeVar("T")


class TestAsyncDependable:
    def test_assertion(self) -> None:
        try:
            dependable(1)  # type: ignore
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        @dependable
        def empty() -> Any:
            return True

        assert await empty()

    @pytest.mark.asyncio
    async def test_arg(self) -> None:
        @dependable
        def _is(*, b: bool) -> bool:
            return b

        assert await _is(b=True)

    @pytest.mark.asyncio
    async def test_depends(self) -> None:
        def falsy() -> bool:
            return False

        @dependable
        def _is(*, actual: bool = Depends(falsy)) -> bool:
            return actual

        assert await _is(actual=True)
        assert not await _is(actual=False)
        assert not await _is()
