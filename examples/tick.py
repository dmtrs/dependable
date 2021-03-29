import asyncio
import time
import uuid
from typing import Tuple

from dependable import Depends, dependant


def get_id() -> uuid.UUID:
    return uuid.uuid4()


async def get_remote_id() -> uuid.UUID:
    await asyncio.sleep(1)
    return uuid.uuid4()


def cpu_bound() -> None:
    time.sleep(1)
    return time.time()


@dependant
async def tick(
    *,
    i: int,
    local_id: uuid.UUID = Depends(get_id),
    remote_id: uuid.UUID = Depends(get_remote_id),
    cpu_time: int = Depends(cpu_bound),
) -> Tuple[int, uuid.UUID, uuid.UUID, int]:
    return (i, local_id, remote_id, cpu_time)


async def main() -> None:
    ticks = set()
    start = time.time()
    print(f"start {start}")
    for i in range(5):
        t = asyncio.create_task(tick(i=i))
        ticks.add(t)
    done, pending = await asyncio.wait(ticks)
    for d in done:
        print(d.result())
    end = time.time()
    print(f"end {end}, duration {end-start}")


asyncio.run(main())
