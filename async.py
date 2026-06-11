import time

from rich import print


def endpoint(route):
    print(f">> handling {route}")

    # emulate database delay
    time.sleep(1)

    print(f"<< response {route}")


def server():
    # Run test request
    tests = (
        "Get /shipment?id=1",
        "Patch /shipment?id=4",
        "Get /shipment?id=3",
    )

    start = time.perf_counter()

    for route in tests:
        endpoint(route)

    end = time.perf_counter()
    print(f"Time taken: {end - start:.2f}s")


# Run Server
server()
