from app.database.models import BlogModel
from app.models.blog import BlogCreate
from app.repositories.blog_repository import BlogRepository


class BlogNotFoundError(Exception):
    pass


class BlogService:
    def __init__(self, repository: BlogRepository):
        self.repository = repository

    def list_blogs(self) -> list[BlogModel]:
        return self.repository.list_blogs()

    def create_blog(self, payload: BlogCreate) -> BlogModel:
        return self.repository.create_blog(title=payload.title, content=payload.content)

    def update_blog(self, blog_id: int, payload: BlogCreate) -> BlogModel:
        blog = self.repository.get_by_id(blog_id)
        if blog is None:
            raise BlogNotFoundError("Blog not found")

        return self.repository.update_blog(blog=blog, title=payload.title, content=payload.content)

    def delete_blog(self, blog_id: int) -> None:
        blog = self.repository.get_by_id(blog_id)
        if blog is None:
            raise BlogNotFoundError("Blog not found")

        self.repository.delete_blog(blog)
