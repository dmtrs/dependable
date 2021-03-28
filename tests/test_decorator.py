from typing import Any, TypeVar

from depends import Depends, dependable

T = TypeVar("T")


class TestDependable:
    def test_empty(self) -> None:
        @dependable
        def empty() -> Any:
            return True

        assert empty()

    def test_arg(self) -> None:
        @dependable
        def _is(b: bool) -> bool:
            return b

        assert _is(True)

    def test_depends(self) -> None:
        def falsy() -> bool:
            return False

        @dependable
        def _is(actual: bool = Depends(falsy)) -> bool:
            return actual

        assert _is(True)
        assert not _is(False)
        # assert not _is()
