from typing import Any

text: str = "value"
pert: int = 90
temp: float = 37.5

number: int | float = 12


shipment: dict[str, Any] = {
    "id": 1234,
    "weight": 1.23,
    "content": "wooden"
}

def root(num: int | float) -> float:
    return pow(num, .5)

root_25 = root(25)