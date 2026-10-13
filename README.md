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
- `GET /api/v1/blogs/{blog_id}`
- `POST /api/v1/blogs`
- `PUT /api/v1/blogs/{blog_id}`
- `DELETE /api/v1/blogs/{blog_id}`

## Architecture (Repository Pattern)

- API layer: `app/api/v1/blogs.py`, `app/api/v1/auth.py`
- Service layer: `app/services/blog_service.py`, `app/services/auth_service.py`
- Repository layer: `app/repositories/blog_repository.py`, `app/repositories/user_repository.py`
- Security helpers (bcrypt, JWT): `app/core/security.py`
- ORM models: `app/database/models.py`

## Authentication (OAuth2 Password Flow + JWT)

Users register with a username, email and password. Passwords are hashed with
bcrypt. Logging in follows the OAuth2 password flow and returns a signed JWT
bearer token, which is sent as `Authorization: Bearer <token>`.

Endpoints:

- `POST /api/v1/auth/register` - create a user (JSON body: `username`, `email`, `password` with 8-72 characters); `201`, or `409` if the username or email is taken
- `POST /api/v1/auth/token` - log in with form data (`username`, `password`); returns `{"access_token": "...", "token_type": "bearer"}`, or `401`
- `GET /api/v1/auth/me` - return the authenticated user; `401` without a valid token

Configuration:

```powershell
$env:JWT_SECRET_KEY="a-long-random-secret"
$env:JWT_ALGORITHM="HS256"
$env:ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

Defaults: `JWT_SECRET_KEY=change-me-in-production` (always override it in production),
`JWT_ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`.

Example:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'

curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=alice&password=secret123"

curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

The `users` table is created by an Alembic migration. Run `alembic -c alembic.ini upgrade head`
before using the auth endpoints. The interactive docs at `/docs` support the "Authorize" button.

Other routers can protect endpoints with the `get_current_user` dependency from `app/api/v1/auth.py`.

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

## Tests

Unit tests use mocks and need no database:

```powershell
python -m pytest
```
