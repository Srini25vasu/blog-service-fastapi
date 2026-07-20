from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class BlogModel(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
