# blog-service-fastapi
Blog service provides content for blogs, posts and comments

## PostgreSQL configuration

Set the `DATABASE_URL` environment variable before running the app.

Example:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/blog_service"
```

Optional production-safe pool settings:

```powershell
$env:DB_POOL_SIZE="10"
$env:DB_MAX_OVERFLOW="20"
$env:DB_POOL_TIMEOUT="30"
$env:DB_POOL_RECYCLE="1800"
$env:DB_POOL_PRE_PING="true"
```

Pool setting defaults:

- `DB_POOL_SIZE=10`
- `DB_MAX_OVERFLOW=20`
- `DB_POOL_TIMEOUT=30`
- `DB_POOL_RECYCLE=1800`
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
