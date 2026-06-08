from typing import Any

from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference


app = FastAPI()

shipments = {
    1234 : {
        "weight": .9,
        "content": "Glass door",
        "status": "Placed" 
    },
    1235 : {
        "weight": 1.2,
        "content": "Wooden chair",
        "status": "In transit"
    },
    1236 : {
        "weight": 2.5,
        "content": "Metal desk",
        "status": "Delivered"
    },
    1237 : {
        "weight": 0.5,
        "content": "Plastic box",
        "status": "Placed"
    },
    1238 : {
        "weight": 3.0,
        "content": "Bookshelf",
        "status": "In transit"
    },
    1239 : {
        "weight": 1.5,
        "content": "Lamp",
        "status": "Delivered"
    },
    1240 : {
        "weight": 2.0,
        "content": "Cabinet",
        "status": "Placed"
    }
}

@app.get("/shipment/latest")
def get_latest_shipment():
    id = max(shipments.keys())
    return shipments[id]


@app.get("/shipment/{id}")
def get_shipment(id: int) -> dict[str, Any]:

    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id does not exist!!"
        )

    return shipments[id]


@app.post("/shipment")
def submit_shipment(data: dict[str, Any]) -> dict[str, Any]:
    content = data["content"]
    weight = data["weight"]

    if weight > 25:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum Weight limit is 25 kgs"
        )

    new_id = max(shipments.keys()) + 1

    shipments[new_id] = {
        "content": content,
        "weight": weight,
        "status": "pending",
    }

    return {"id": new_id}


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
