# blog-service-fastapi

Blog service provides content for blogs, posts and comments

## PostgreSQL configuration

You can configure PostgreSQL in either of these ways before running the app.

Option 1: provide the full `DATABASE_URL`.

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/blog_service?options=-csearch_path%3Dblogs-python"
```

Option 2: provide individual connection parts. This is useful when your PostgreSQL server is running in Docker and you want to keep credentials separate.

```powershell
$env:DB_USER="postgres"
$env:DB_PASSWORD="postgres"
$env:DB_HOST="host.docker.internal"
$env:DB_PORT="49153"
$env:DB_NAME="blogdb"
$env:DB_SCHEMA="blogs-python"
```

If `DATABASE_URL` is set, it takes precedence over the individual `DB_*` variables.
If you still have an older URL using `currentSchema=...`, the app now normalizes it automatically for psycopg2.

Optional production-safe pool settings:

```powershell
$env:DB_POOL_SIZE="20"
$env:DB_MAX_OVERFLOW="40"
$env:DB_POOL_TIMEOUT="45"
$env:DB_POOL_RECYCLE="1500"
$env:DB_POOL_PRE_PING="true"
```

Pool setting defaults:

- `DB_POOL_SIZE=20`
- `DB_MAX_OVERFLOW=40`
- `DB_POOL_TIMEOUT=45`
- `DB_POOL_RECYCLE=1500`
- `DB_POOL_PRE_PING=true`

Create database once in PostgreSQL:

```sql
CREATE DATABASE blog_service;
```

The blogs endpoints now persist to PostgreSQL:

- `GET /api/v1/blogs`
- `POST /api/v1/blogs`
- `PUT /api/v1/blogs/{blog_id}`
- `DELETE /api/v1/blogs/{blog_id}`

## Architecture (Repository Pattern)

- API layer: `app/api/v1/blogs.py`
- Service layer: `app/services/blog_service.py`
- Repository layer: `app/repositories/blog_repository.py`
- ORM models: `app/database/models.py`

## Alembic Migrations

Run migrations:

```powershell
alembic -c alembic.ini upgrade head
```

Create a new migration after schema changes:

```powershell
alembic -c alembic.ini revision --autogenerate -m "describe change"
```

Rollback one migration:

```powershell
alembic -c alembic.ini downgrade -1
```
