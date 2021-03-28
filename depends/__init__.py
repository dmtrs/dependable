__author__ = """Dimitrios Flaco Mengidis """
__email__ = "tydeas.dr@gmail.com"
__version__ = "0.1.0"

from typing import Any, Callable, Optional

from .core import Depends as InternalDepends
from .decorator import dependable as dependable


def Depends(  # noqa: N802
    dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = True
) -> Any:
    return InternalDepends(dependency=dependency, use_cache=use_cache)
