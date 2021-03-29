import asyncio
from random import random

from dependable import Depends, dependant


@dependant
async def main(*, choice: int = Depends(random)) -> None:
    print(choice)


asyncio.run(main())
