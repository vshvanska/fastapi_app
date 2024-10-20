from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.comments.models import Comment
from src.models import BaseModel


class Post(BaseModel):
    __tablename__ = "post"

    title: Mapped[str] = mapped_column(String(30))
    content: Mapped[str]
    auto_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_text: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    comments: Mapped[List[Comment]] = relationship(
        Comment, back_populates="post", cascade="all, delete-orphan"
    )

    user = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"Owner id: {self.user_id} - {self.title}"
