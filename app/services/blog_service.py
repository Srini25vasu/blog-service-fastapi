"""Business logic for blogs.

The service sits between the API layer and the repository: routes call the
service, and the service talks to the database only through ``BlogRepository``.
Domain errors are raised as exceptions (e.g. ``BlogNotFoundError``) and are
translated into HTTP responses by the API layer.
"""

from app.database.models import BlogModel
from app.models.blog import BlogCreate
from app.repositories.blog_repository import BlogRepository


class BlogNotFoundError(Exception):
    """Raised when a blog with the requested id does not exist."""

    def __init__(self, blog_id: int) -> None:
        self.blog_id = blog_id
        super().__init__(f"Blog with id {blog_id} not found")


class BlogService:
    """Use cases for creating, reading, updating and deleting blogs."""

    def __init__(self, repository: BlogRepository) -> None:
        """Create the service.

        Args:
            repository: Data access object used to persist blogs.
        """
        self.repository = repository

    def list_blogs(self) -> list[BlogModel]:
        """Return all blogs.

        Returns:
            Every stored blog; an empty list if there are none.
        """
        return self.repository.list_blogs()

    def get_blog(self, blog_id: int) -> BlogModel:
        """Return a single blog by its id.

        Args:
            blog_id: Primary key of the blog.

        Returns:
            The matching blog.

        Raises:
            BlogNotFoundError: If no blog with ``blog_id`` exists.
        """
        return self._get_blog_or_raise(blog_id)

    def create_blog(self, payload: BlogCreate) -> BlogModel:
        """Create and persist a new blog.

        Args:
            payload: Validated title and content of the new blog.

        Returns:
            The created blog, including its generated id.
        """
        return self.repository.create_blog(title=payload.title, content=payload.content)

    def update_blog(self, blog_id: int, payload: BlogCreate) -> BlogModel:
        """Replace the title and content of an existing blog.

        Args:
            blog_id: Primary key of the blog to update.
            payload: New title and content.

        Returns:
            The updated blog.

        Raises:
            BlogNotFoundError: If no blog with ``blog_id`` exists.
        """
        blog = self._get_blog_or_raise(blog_id)
        return self.repository.update_blog(blog=blog, title=payload.title, content=payload.content)

    def delete_blog(self, blog_id: int) -> None:
        """Delete an existing blog.

        Args:
            blog_id: Primary key of the blog to delete.

        Raises:
            BlogNotFoundError: If no blog with ``blog_id`` exists.
        """
        blog = self._get_blog_or_raise(blog_id)
        self.repository.delete_blog(blog)

    def _get_blog_or_raise(self, blog_id: int) -> BlogModel:
        """Load a blog or raise ``BlogNotFoundError`` if it does not exist."""
        blog = self.repository.get_by_id(blog_id)
        if blog is None:
            raise BlogNotFoundError(blog_id)
        return blog
