import time
import asyncio

from rich import print


async def endpoint(route: str) -> str:
    print(f">> handling {route}")

    # emulate database delay
    await asyncio.sleep(1)

    print(f"<< response {route}")
    return route


async def server():
    # Run test request
    tests = (
        "Get /shipment?id=1",
        "Patch /shipment?id=4",
        "Get /shipment?id=3",
    )

    start = time.perf_counter()

    for route in tests:
        result = await endpoint(route)
        print("Result back: ", result)

    end = time.perf_counter()
    print(f"Time taken: {end - start:.2f}s")


# Run Server
asyncio.run(server())
