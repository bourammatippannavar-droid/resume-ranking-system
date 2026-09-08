import logging

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.candidates import router as candidates_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.search import router as search_router
from app.core.config import get_settings


settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(search_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError:
        logger.exception("Database health check failed")
        return {"status": "error", "database": "error"}
