<h1 align="center">
    <strong>dependable</strong>
</h1>
<p align="center">
    <a href="https://github.com/dmtrs/dependable" target="_blank">
        <img src="https://img.shields.io/github/last-commit/dmtrs/dependable" alt="Latest Commit">
    </a>
        <img src="https://img.shields.io/github/workflow/status/dmtrs/dependable/Test">
        <img src="https://img.shields.io/codecov/c/github/dmtrs/dependable">
    <br />
    <a href="https://pypi.org/project/dependable" target="_blank">
        <img src="https://img.shields.io/pypi/v/dependable" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/dependable">
    <img src="https://img.shields.io/github/license/dmtrs/dependable">
</p>

Dependency injection system extracted from `fastapi`

```python
import asyncio
from random import random

from dependable import dependant, Depends

@dependant
async def main(*, choice: int = Depends(random)) -> None:
    print(choice)

asyncio.run(main())
```

More on [examples](examples/tick.py)

## Installation

``` bash
poetry add dependable # pip install dependable
```

## Python 3.6

- Backport require of [async-exit-stack](https://pypi.org/project/async-exit-stack/) and [async_generator](https://pypi.org/project/async_generator/)
```bash
poetry add async-exit-stack async_generator # pip install async-exit-stack async_generator
```

## Development

```bash
docker build -t dependable .
```

```bash
docker run --rm -v $(pwd):/usr/src/app dependable scripts/dev
```

## References

- [tiangolo/fastapi#2967](https://github.com/tiangolo/fastapi/issues/2967)

## License

This project is licensed under the terms of the MIT license.
