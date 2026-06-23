from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.api.tag import APITag
from app.core.exceptions import add_exception_handlers
from app.worker.tasks import add_log


description = """
Delivery Management System for sellers and agents

### Seller
- Submit shiment effortlessly
- Share tracking links with customers

### Delivery Agent
- Auto accept shipments
- Track and update status
- Email and SMS notification
"""

app = FastAPI(
    title="FastShip",
    description=description,
    version="0.1.0",
    terms_of_service="https://fastapi.tiangolo.com/terms/",
    contact={
        "name": "FastShip Support",
        "url": "https://fastship.com/support",
        "email": "support@fastship.com",
    },
    openapi_tags=[
        {
            "name": APITag.SHIPMENT,
            "description": "Operations related to shipment",
        },
        {
            "name": APITag.SELLER,
            "description": "Operations related to the seller",
        },
        {
            "name": APITag.PARTNER,
            "description": "Operations related to the delivery partner",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["*"],
)

app.include_router(master_router)

add_exception_handlers(app)


# Add custom middleware
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start = perf_counter()

    response: Response = await call_next(request)

    end = perf_counter()
    time_taken = round(end - start, 2)

    add_log.delay(
        f"{request.method} {request.url} ({response.status_code}) {time_taken} s"
    )

    return response


@app.get("/")
def read_root():
    return {"detail": "server is running...."}


### Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
