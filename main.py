import logging

from fastapi import FastAPI
from sqlalchemy.engine import make_url

from app.api.v1 import blogs
from app.config.settings import (
    DATABASE_URL,
    DB_MAX_OVERFLOW,
    DB_POOL_PRE_PING,
    DB_POOL_RECYCLE,
    DB_POOL_SIZE,
    DB_POOL_TIMEOUT,
)

app = FastAPI(title="Blog Service API", version="1.0.0")
logger = logging.getLogger("app.startup")


@app.on_event("startup")
def log_db_pool_settings() -> None:
    sanitized_db_url = make_url(DATABASE_URL).render_as_string(hide_password=True)
    logger.info("Database URL: %s", sanitized_db_url)
    logger.info(
        "DB pool settings: size=%s max_overflow=%s timeout=%ss recycle=%ss pre_ping=%s",
        DB_POOL_SIZE,
        DB_MAX_OVERFLOW,
        DB_POOL_TIMEOUT,
        DB_POOL_RECYCLE,
        DB_POOL_PRE_PING,
    )

# Include routers
app.include_router(blogs.router, prefix="/api/v1", tags=["blogs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)