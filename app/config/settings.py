import os
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit


DB_DRIVER = os.getenv("DB_DRIVER", "postgresql+psycopg2")
DB_HOST = os.getenv("DB_HOST", "host.docker.internal")
DB_PORT = os.getenv("DB_PORT", "49153")
DB_NAME = os.getenv("DB_NAME", "blogdb")
DB_SCHEMA = os.getenv("DB_SCHEMA", "blogs-python")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def _int_env(name: str, default: int, *, minimum: int = 0) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        parsed = int(value)
    except ValueError:
        return default

    return max(parsed, minimum)


def _normalize_database_url(database_url: str) -> str:
    parsed_url = urlsplit(database_url)
    query_params = parse_qsl(parsed_url.query, keep_blank_values=True)

    current_schema = None
    normalized_query_params = []
    has_options = False
    for key, value in query_params:
        if key == "currentSchema":
            current_schema = value
            continue
        if key == "options":
            has_options = True
        normalized_query_params.append((key, value))

    if current_schema and not has_options:
        normalized_query_params.append(("options", f"-csearch_path={current_schema}"))

    return urlunsplit(parsed_url._replace(query=urlencode(normalized_query_params)))


def _build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return _normalize_database_url(database_url)

    auth = ""
    if DB_USER:
        auth = quote_plus(DB_USER)
        if DB_PASSWORD is not None:
            auth = f"{auth}:{quote_plus(DB_PASSWORD)}"
        auth = f"{auth}@"

    schema = f"?options={quote_plus(f'-csearch_path={DB_SCHEMA}')}" if DB_SCHEMA else ""
    return f"{DB_DRIVER}://{auth}{DB_HOST}:{DB_PORT}/{DB_NAME}{schema}"


DATABASE_URL = _build_database_url()


DB_POOL_SIZE = _int_env("DB_POOL_SIZE", 20, minimum=1)
DB_MAX_OVERFLOW = _int_env("DB_MAX_OVERFLOW", 40, minimum=0)
DB_POOL_TIMEOUT = _int_env("DB_POOL_TIMEOUT", 45, minimum=1)
DB_POOL_RECYCLE = _int_env("DB_POOL_RECYCLE", 1500, minimum=30)
DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
