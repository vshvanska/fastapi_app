from typing import Optional, List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column
from src.models import BaseModel


class Comment(BaseModel):
    __tablename__ = "comment"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(150))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    parent_id: Optional[Mapped[int]] = mapped_column(
        ForeignKey("comment.id"), nullable=True
    )

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    children: List["Comment"] = relationship(
        "Comment", back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Optional["Comment"] = relationship(
        "Comment", remote_side=[id], back_populates="children"
    )

    def __repr__(self):
        return f"User {self.user_id}: {self.content}"
