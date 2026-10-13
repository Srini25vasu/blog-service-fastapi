import logging

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.api.v1 import auth, blogs
from app.config.settings import (
    API_V1_PREFIX,
    DATABASE_URL,
    DB_MAX_OVERFLOW,
    DB_POOL_PRE_PING,
    DB_POOL_RECYCLE,
    DB_POOL_SIZE,
    DB_POOL_TIMEOUT,
    check_jwt_secret_key,
)
from app.database.session import engine

app = FastAPI(title="Blog Service API", version="1.0.0")
logger = logging.getLogger("app.startup")


@app.on_event("startup")
def check_jwt_settings() -> None:
    jwt_warning = check_jwt_secret_key()
    if jwt_warning:
        logger.warning(jwt_warning)


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
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logger.info("Database connection established successfully")

# Include routers
app.include_router(blogs.router, prefix=API_V1_PREFIX, tags=["blogs"])
app.include_router(auth.router, prefix=API_V1_PREFIX, tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)