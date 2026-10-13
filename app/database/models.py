from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.settings import DB_SCHEMA
from app.database.session import Base


class BlogModel(Base):
    __tablename__ = "blogs"
    __table_args__ = {"schema": DB_SCHEMA} if DB_SCHEMA else {}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": DB_SCHEMA} if DB_SCHEMA else {}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
