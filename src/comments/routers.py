from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from src.comments.tasks import create_reply_comment
from src.auth.auth import Authenticator
from src.comments.schemas import CommentBase, Comment, CommentRead, CommentUpdate
from src.config import settings
from src.dependencies import (
    get_authenticator,
    get_comment_repository,
    get_async_session, get_post_repository,
)
from src.posts.repository import PostRepository
from src.repositories import AbstractRepository

comment_router = APIRouter(tags=["Comments"], prefix="/comments")


@comment_router.post("", response_model=Comment)
async def create_comment(
    data: CommentBase,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    repository: AbstractRepository = Depends(get_comment_repository),
    post_repository: PostRepository = Depends(get_post_repository),
    session: AsyncSession = Depends(get_async_session),
):
    data = data.model_dump()
    post = await post_repository.get_instance(id=data["post_id"], session=session)
    if not post:
        raise HTTPException(status_code=404, detail="Invalid data")
    if data.get("parent_id"):
        parent = await repository.get_instance(id=data["parent_id"], session=session)
        if not parent:
            raise HTTPException(status_code=404, detail="Invalid data")
    token_data = await authenticator.check_if_authenticated(token=token)
    data["user_id"] = token_data.id
    instance = await repository.create_instance(data=data, session=session)
    if post and post.auto_reply:
        reply_comment = {"content": post.reply_text, "post_id": post.id, "user_id": post.user_id, "parent_id": instance.id}
        create_reply_comment.delay(reply_comment)
    return instance


@comment_router.get("", response_model=List[Comment])
async def get_comments(
    post_id: int,
    repository: AbstractRepository = Depends(get_comment_repository),
    session: AsyncSession = Depends(get_async_session),
):
    posts = await repository.get_list(session=session, post_id=post_id)
    return posts


@comment_router.get("/my", response_model=List[CommentRead])
async def get_my_comments(
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    repository: AbstractRepository = Depends(get_comment_repository),
    session: AsyncSession = Depends(get_async_session),
):
    token_data = await authenticator.check_if_authenticated(token=token)
    user_id = token_data.id
    comments = await repository.get_list(session=session, user_id=user_id)
    return comments


@comment_router.put("/{comment_id}", response_model=CommentUpdate)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    repository: AbstractRepository = Depends(get_comment_repository),
    session: AsyncSession = Depends(get_async_session),
):
    token_data = await authenticator.check_if_authenticated(token=token)
    instance = await repository.get_instance(id=comment_id, session=session)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    if token_data.id != instance.user_id:
        raise HTTPException(status_code=404, detail="Incorrect credentials")

    updated_instance = await repository.update_instance(
        id=comment_id, data=data, session=session
    )
    return updated_instance


@comment_router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    repository: AbstractRepository = Depends(get_comment_repository),
    session: AsyncSession = Depends(get_async_session),
):
    token_data = await authenticator.check_if_authenticated(token=token)
    instance = await repository.get_instance(id=comment_id, session=session)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    if token_data.id != instance.user_id:
        raise HTTPException(status_code=404, detail="Incorrect credentials")

    await repository.delete_instance(id=comment_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT, content="Comment deleted"
    )
