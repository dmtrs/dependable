from dependable import Depends


class TestDepends:
    def test_repr(self) -> None:
        def get_user() -> None:
            pass  # pragma: no cover

        assert repr(Depends()) == "Depends(NoneType, use_cache=False)"
        assert repr(Depends(get_user)) == "Depends(get_user, use_cache=False)"
        assert repr(Depends(use_cache=True)) == "Depends(NoneType, use_cache=True)"
        assert repr(Depends(get_user)) == "Depends(get_user, use_cache=False)"
