from sqlalchemy.orm import Session

from app.database.models import BlogModel


class BlogRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_blogs(self) -> list[BlogModel]:
        return self.db.query(BlogModel).all()

    def get_by_id(self, blog_id: int) -> BlogModel | None:
        return self.db.query(BlogModel).filter(BlogModel.id == blog_id).first()

    def create_blog(self, title: str, content: str) -> BlogModel:
        blog = BlogModel(title=title, content=content)
        self.db.add(blog)
        self.db.commit()
        self.db.refresh(blog)
        return blog

    def update_blog(self, blog: BlogModel, title: str, content: str) -> BlogModel:
        blog.title = title
        blog.content = content
        self.db.commit()
        self.db.refresh(blog)
        return blog

    def delete_blog(self, blog: BlogModel) -> None:
        self.db.delete(blog)
        self.db.commit()
