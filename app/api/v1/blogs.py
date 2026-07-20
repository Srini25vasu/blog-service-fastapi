from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.blog import Blog, BlogCreate
from app.repositories.blog_repository import BlogRepository
from app.services.blog_service import BlogNotFoundError, BlogService

router = APIRouter()


def get_blog_service(db: Session = Depends(get_db)) -> BlogService:
    repository = BlogRepository(db)
    return BlogService(repository)

@router.get("/blogs")
def get_blogs(service: BlogService = Depends(get_blog_service)):
    return service.list_blogs()


@router.post("/blogs", status_code=status.HTTP_201_CREATED, response_model=Blog)
def create_blog(payload: BlogCreate, service: BlogService = Depends(get_blog_service)):
    return service.create_blog(payload)


@router.put("/blogs/{blog_id}", response_model=Blog)
def update_blog(blog_id: int, payload: BlogCreate, service: BlogService = Depends(get_blog_service)):
    try:
        return service.update_blog(blog_id, payload)
    except BlogNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found") from exc


@router.delete("/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int, service: BlogService = Depends(get_blog_service)):
    try:
        service.delete_blog(blog_id)
    except BlogNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found") from exc

    return None
