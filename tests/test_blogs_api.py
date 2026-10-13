"""Unit tests for the blog routes in ``app.api.v1.blogs``.

The router is mounted on a fresh FastAPI app (instead of ``main.app``) so the
startup DB check does not run, and ``get_blog_service`` is overridden with a
mocked service. These tests cover HTTP status codes, response bodies and the
mapping of ``BlogNotFoundError`` to 404.
"""

from unittest.mock import create_autospec

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import blogs
from app.database.models import BlogModel
from app.models.blog import BlogCreate
from app.services.blog_service import BlogNotFoundError, BlogService


@pytest.fixture
def service():
    return create_autospec(BlogService, instance=True)


@pytest.fixture
def client(service):
    app = FastAPI()
    app.include_router(blogs.router, prefix="/api/v1")
    app.dependency_overrides[blogs.get_blog_service] = lambda: service
    return TestClient(app)


@pytest.fixture
def blog():
    return BlogModel(id=1, title="First post", content="Hello world")


BLOG_JSON = {"id": 1, "title": "First post", "content": "Hello world"}


def test_get_blogs_returns_list(client, service, blog):
    service.list_blogs.return_value = [blog]

    response = client.get("/api/v1/blogs")

    assert response.status_code == 200
    assert response.json() == [BLOG_JSON]


def test_get_blog_returns_blog(client, service, blog):
    service.get_blog.return_value = blog

    response = client.get("/api/v1/blogs/1")

    assert response.status_code == 200
    assert response.json() == BLOG_JSON
    service.get_blog.assert_called_once_with(1)


def test_get_blog_returns_404_when_missing(client, service):
    service.get_blog.side_effect = BlogNotFoundError(42)

    response = client.get("/api/v1/blogs/42")

    assert response.status_code == 404
    assert response.json() == {"detail": "Blog not found"}


def test_get_blog_returns_422_for_non_integer_id(client, service):
    response = client.get("/api/v1/blogs/abc")

    assert response.status_code == 422
    service.get_blog.assert_not_called()


def test_create_blog_returns_201(client, service, blog):
    service.create_blog.return_value = blog

    response = client.post("/api/v1/blogs", json={"title": "First post", "content": "Hello world"})

    assert response.status_code == 201
    assert response.json() == BLOG_JSON
    service.create_blog.assert_called_once_with(BlogCreate(title="First post", content="Hello world"))


def test_create_blog_returns_422_for_invalid_payload(client, service):
    response = client.post("/api/v1/blogs", json={"title": "Missing content"})

    assert response.status_code == 422
    service.create_blog.assert_not_called()


def test_update_blog_returns_updated_blog(client, service, blog):
    service.update_blog.return_value = blog

    response = client.put("/api/v1/blogs/1", json={"title": "First post", "content": "Hello world"})

    assert response.status_code == 200
    assert response.json() == BLOG_JSON
    service.update_blog.assert_called_once_with(1, BlogCreate(title="First post", content="Hello world"))


def test_update_blog_returns_404_when_missing(client, service):
    service.update_blog.side_effect = BlogNotFoundError(42)

    response = client.put("/api/v1/blogs/42", json={"title": "t", "content": "c"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Blog not found"}


def test_delete_blog_returns_204(client, service):
    response = client.delete("/api/v1/blogs/1")

    assert response.status_code == 204
    assert response.content == b""
    service.delete_blog.assert_called_once_with(1)


def test_delete_blog_returns_404_when_missing(client, service):
    service.delete_blog.side_effect = BlogNotFoundError(42)

    response = client.delete("/api/v1/blogs/42")

    assert response.status_code == 404
