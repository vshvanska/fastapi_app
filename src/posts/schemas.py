from typing import Optional
from pydantic import ConfigDict, BaseModel
from src.auth.schemas import UserPost
from src.schemas import BaseInstance


class PostBase(BaseModel):
    title: str
    content: str
    auto_reply: Optional[bool] = False
    reply_text: Optional[str] = None


class Post(PostBase, BaseInstance):
    id: int
    user_id: int


class PostList(PostBase, BaseInstance):
    id: int
    is_active: bool
    user: UserPost

    model_config = ConfigDict(from_attributes=True)


class PostComment(BaseInstance):
    id: int
    title: str
    user: UserPost

    model_config = ConfigDict(from_attributes=True)
