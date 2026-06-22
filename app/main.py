from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import BackgroundTasks, FastAPI, Request, Response
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.core.exceptions import add_exception_handlers
from app.database.session import create_db_tables
from app.services.notification import NotificationService
from app.worker.tasks import add_log


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI()
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


@app.get("/mail")
async def send_test_mail(tasks: BackgroundTasks):

    tasks.add_task(
        NotificationService(tasks).send_email,
        recipients=["pyzegv@mailto.plus"],
        subject="Test mail coming through once",
        body="Hello this is vladmir. I eat fluffy dolls and terdy bears for funn. hwahwha😂😂😒",
    )

    return {"detail": "Sending mail..."}


### Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
