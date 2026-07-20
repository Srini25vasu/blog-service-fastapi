from pydantic import BaseModel, ConfigDict


class BlogCreate(BaseModel):
    title: str
    content: str


class Blog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str