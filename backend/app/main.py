from fastapi import FastAPI

from app.api.middleware.logging import log_requests
from app.api.v1.router import router
from app.core.config import settings
from app.core.logging import logger
from app.database.connection import check_database_connection

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)


app.middleware("http")(log_requests)


app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    if not check_database_connection():
        raise RuntimeError("Cannot connect to database")
    logger.info("LifeOS API started")
