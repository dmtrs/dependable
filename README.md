<h1 align="center">
    <strong>depends</strong>
</h1>
<p align="center">
    <a href="https://github.com/dmtrs/depends" target="_blank">
        <img src="https://img.shields.io/github/last-commit/dmtrs/depends" alt="Latest Commit">
    </a>
        <img src="https://img.shields.io/github/workflow/status/dmtrs/depends/Test">
        <img src="https://img.shields.io/codecov/c/github/dmtrs/depends">
    <br />
    <a href="https://pypi.org/project/depends" target="_blank">
        <img src="https://img.shields.io/pypi/v/depends" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/depends">
    <img src="https://img.shields.io/github/license/dmtrs/depends">
</p>

Dependency injection system extracted from `fastapi`

```python
import asyncio
from random import random

from depends import Depends, dependable

@dependable
async def main(*, choice: int = Depends(random)) -> None:
    print(choice)

asyncio.run(main())
```

## Installation

``` bash
poetry add depends # pip install depends
```

## Python 3.6

- Backport require of [async-exit-stack](https://pypi.org/project/async-exit-stack/) and [async_generator](https://pypi.org/project/async_generator/)
```bash
poetry add async-exit-stack async_generator # pip install async-exit-stack async_generator
```

## Development

```bash
docker build -t depends .
```

```bash
docker run --rm -v $(pwd):/usr/src/app depends scripts/dev
```

## References

- [tiangolo/fastapi#2967](https://github.com/tiangolo/fastapi/issues/2967)

## License

This project is licensed under the terms of the MIT license.
