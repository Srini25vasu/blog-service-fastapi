"""HTTP routes for the blogs resource (``/api/v1/blogs``)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.blog import Blog, BlogCreate
from app.repositories.blog_repository import BlogRepository
from app.services.blog_service import BlogNotFoundError, BlogService

router = APIRouter()


def get_blog_service(db: Session = Depends(get_db)) -> BlogService:
    """Build a ``BlogService`` bound to the current request's DB session."""
    repository = BlogRepository(db)
    return BlogService(repository)


@router.get("/blogs", response_model=list[Blog])
def get_blogs(service: BlogService = Depends(get_blog_service)):
    """List all blogs."""
    return service.list_blogs()


@router.get("/blogs/{blog_id}", response_model=Blog)
def get_blog(blog_id: int, service: BlogService = Depends(get_blog_service)):
    """Return a single blog, or 404 if it does not exist."""
    try:
        return service.get_blog(blog_id)
    except BlogNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found") from exc


@router.post("/blogs", status_code=status.HTTP_201_CREATED, response_model=Blog)
def create_blog(payload: BlogCreate, service: BlogService = Depends(get_blog_service)):
    """Create a new blog."""
    return service.create_blog(payload)


@router.put("/blogs/{blog_id}", response_model=Blog)
def update_blog(blog_id: int, payload: BlogCreate, service: BlogService = Depends(get_blog_service)):
    """Replace a blog's title and content, or 404 if it does not exist."""
    try:
        return service.update_blog(blog_id, payload)
    except BlogNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found") from exc


@router.delete("/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int, service: BlogService = Depends(get_blog_service)):
    """Delete a blog, or 404 if it does not exist."""
    try:
        service.delete_blog(blog_id)
    except BlogNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found") from exc

    return None
