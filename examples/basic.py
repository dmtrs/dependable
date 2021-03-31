#!/bin/sh
import time
import uuid
import yappi

import asyncio
from typing import Tuple

from dependable import Depends, dependant

async def some_service() -> uuid.UUID:
    await asyncio.sleep(1)
    return uuid.uuid4()

async def main() -> Tuple[uuid.UUID, uuid.UUID]:
    _id: uuid.UUID = await some_service()
    other_id: uuid.UUID = await some_service()
    return (_id, other_id)

@dependant
async def main_with_depends(
    *,
    _id: uuid.UUID = Depends(some_service),
    other_id: uuid.UUID = Depends(some_service),
) -> Tuple[uuid.UUID, uuid.UUID]:
    return (_id, other_id)

yappi.set_clock_type("cpu")
"""
with yappi.run():
    for i in range(5):
        asyncio.run(main())

yappi.get_func_stats().print_all()
"""
with yappi.run():
    for i in range(5):
        asyncio.run(main_with_depends())

yappi.get_func_stats().print_all()
