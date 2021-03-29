import asyncio
from random import random

from depends import Depends, dependable


@dependable
async def main(*, choice: int = Depends(random)) -> None:
    print(choice)


asyncio.run(main())
