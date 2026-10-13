"""Unit tests for ``BlogService``.

The repository is replaced by an autospec mock, so these tests run without a
database and only verify the service's own logic.
"""

from unittest.mock import create_autospec

import pytest

from app.database.models import BlogModel
from app.models.blog import BlogCreate
from app.repositories.blog_repository import BlogRepository
from app.services.blog_service import BlogNotFoundError, BlogService


@pytest.fixture
def repository():
    """Mocked repository whose methods enforce the real signatures."""
    return create_autospec(BlogRepository, instance=True)


@pytest.fixture
def service(repository):
    return BlogService(repository)


@pytest.fixture
def blog():
    return BlogModel(id=1, title="First post", content="Hello world")


def test_list_blogs_returns_all_blogs(service, repository, blog):
    repository.list_blogs.return_value = [blog]

    assert service.list_blogs() == [blog]
    repository.list_blogs.assert_called_once_with()


def test_list_blogs_returns_empty_list_when_no_blogs(service, repository):
    repository.list_blogs.return_value = []

    assert service.list_blogs() == []


def test_get_blog_returns_blog(service, repository, blog):
    repository.get_by_id.return_value = blog

    assert service.get_blog(1) is blog
    repository.get_by_id.assert_called_once_with(1)


def test_get_blog_raises_when_missing(service, repository):
    repository.get_by_id.return_value = None

    with pytest.raises(BlogNotFoundError) as exc_info:
        service.get_blog(42)

    assert exc_info.value.blog_id == 42
    assert "42" in str(exc_info.value)


def test_create_blog_passes_payload_to_repository(service, repository, blog):
    repository.create_blog.return_value = blog
    payload = BlogCreate(title="First post", content="Hello world")

    assert service.create_blog(payload) is blog
    repository.create_blog.assert_called_once_with(title="First post", content="Hello world")


def test_update_blog_updates_existing_blog(service, repository, blog):
    repository.get_by_id.return_value = blog
    repository.update_blog.return_value = blog
    payload = BlogCreate(title="New title", content="New content")

    assert service.update_blog(1, payload) is blog
    repository.update_blog.assert_called_once_with(blog=blog, title="New title", content="New content")


def test_update_blog_raises_when_missing(service, repository):
    repository.get_by_id.return_value = None
    payload = BlogCreate(title="New title", content="New content")

    with pytest.raises(BlogNotFoundError):
        service.update_blog(42, payload)

    repository.update_blog.assert_not_called()


def test_delete_blog_deletes_existing_blog(service, repository, blog):
    repository.get_by_id.return_value = blog

    assert service.delete_blog(1) is None
    repository.delete_blog.assert_called_once_with(blog)


def test_delete_blog_raises_when_missing(service, repository):
    repository.get_by_id.return_value = None

    with pytest.raises(BlogNotFoundError):
        service.delete_blog(42)

    repository.delete_blog.assert_not_called()
