from fastapi import APIRouter
from app.models.blog import Blog

router = APIRouter()

blogs = [Blog(id=1, title="My first blog", content="This is my first blog"),
    Blog(id=2, title="My second blog", content="This is my second blog"),
    Blog(id=3, title="My third blog", content="This is my third blog")]

@router.get("/blogs")
def get_blogs():
    return blogs
