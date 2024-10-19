from datetime import date
from typing import Optional, List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.comments.models import Comment
from src.models import BaseModel
from src.posts.models import Post


class User(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    birthdate: Mapped[Optional[date]]
    hashed_password: Mapped[str] = mapped_column(String)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    posts: Mapped[List[Post]] = relationship(
        Post, back_populates="user", cascade="all, delete-orphan"
    )
    comments: Mapped[List[Comment]] = relationship(
        Comment, back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return {self.username}
