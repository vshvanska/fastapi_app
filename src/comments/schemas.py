from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.auth.schemas import UserPost
from src.posts.schemas import PostComment
from src.schemas import BaseInstance


class CommentBase(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    content: str


class Comment(CommentBase, BaseInstance):
    id: int
    user_id: int


class CommentRead(BaseInstance):
    content: str
    is_active: bool
    parent_id: Optional[int] = None
    post: PostComment
    user: UserPost

    model_config = ConfigDict(from_attributes=True)
