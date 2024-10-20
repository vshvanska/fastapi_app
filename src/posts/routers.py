from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.auth.auth import Authenticator
from src.config import settings
from src.dependencies import get_authenticator, get_post_repository, get_async_session
from src.posts.repository import PostRepository
from src.posts.schemas import Post, PostBase, PostList

post_router = APIRouter(tags=["Posts"], prefix="/posts")


@post_router.post("", response_model=Post)
async def create_post(
    data: PostBase,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    session: AsyncSession = Depends(get_async_session),
    repository: PostRepository = Depends(get_post_repository),
):

    token_data = await authenticator.check_if_authenticated(token=token)
    data = data.model_dump()
    data["user_id"] = token_data.id
    instance = await repository.create_instance(data=data, session=session)
    return instance


@post_router.get("", response_model=List[PostList])
async def get_posts(
    username: Optional[str] = None,
    title: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    repository: PostRepository = Depends(get_post_repository),
):
    posts = await repository.get_list(username=username, title=title, session=session)
    return posts


@post_router.get("/my", response_model=List[PostList])
async def get_personal_posts(
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    session: AsyncSession = Depends(get_async_session),
    repository: PostRepository = Depends(get_post_repository),
):

    token_data = await authenticator.check_if_authenticated(token=token)
    user_id = token_data.id
    posts = await repository.get_list(user_id=user_id, session=session)
    return posts


@post_router.put("/{post_id}", response_model=PostBase)
async def update_post(
    post_id: int,
    data: PostBase,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    session: AsyncSession = Depends(get_async_session),
    repository: PostRepository = Depends(get_post_repository),
):
    token_data = await authenticator.check_if_authenticated(token=token)
    instance = await repository.get_instance(id=post_id, session=session)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST, detail="Instance not found"
        )

    if token_data.id != instance.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
        )

    updated_instance = await repository.update_instance(
        id=post_id, data=data, session=session
    )
    return updated_instance


@post_router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    session: AsyncSession = Depends(get_async_session),
    repository: PostRepository = Depends(get_post_repository),
):
    token_data = await authenticator.check_if_authenticated(token=token)
    instance = await repository.get_instance(id=post_id, session=session)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    if token_data.id != instance.user_id:
        raise HTTPException(status_code=404, detail="Incorrect credentials")

    await repository.delete_instance(id=post_id, session=session)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="Post deleted")
