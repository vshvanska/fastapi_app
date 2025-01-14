from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.auth import Authenticator
from src.auth.schemas import AccessToken, User, TokenPair, UserBase
from src.auth.repository import UserRepository
from src.auth.schemas import UserCreate
from src.config import settings
from src.dependencies import get_user_repository, get_async_session, get_authenticator
from src.repositories import AbstractRepository

user_router = APIRouter(tags=["Users"], prefix="/users")


@user_router.post("/", name="users:register-user")
async def register_user(
    user: UserCreate,
    repository: UserRepository = Depends(get_user_repository),
    session=Depends(get_async_session),
):
    return await repository.create_instance(data=user, session=session)


@user_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    authenticator=Depends(get_authenticator),
    repository: UserRepository = Depends(get_user_repository),
    session=Depends(get_async_session),
) -> TokenPair:
    user = await authenticator.authenticate_user(
        form_data.username, form_data.password, repository, session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = await authenticator.create_pair_token(
        data={"sub": user.username, "id": user.id},
    )
    return token_data


@user_router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    token: str,
    authenticator: Authenticator = Depends(get_authenticator),
):
    token = await authenticator.refresh_access_token(token=token)
    return token


@user_router.get("/me", response_model=User)
async def read_users_me(
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    repository: AbstractRepository = Depends(get_user_repository),
    session: AsyncSession = Depends(get_async_session),
):
    return await authenticator.get_current_user(
        token=token, repository=repository, session=session
    )


@user_router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    data: UserBase,
    token: Annotated[str, Depends(settings.oauth2_scheme)],
    authenticator: Authenticator = Depends(get_authenticator),
    repository: AbstractRepository = Depends(get_user_repository),
    session: AsyncSession = Depends(get_async_session),
):
    token_data = await authenticator.check_if_authenticated(token=token)
    if token_data.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
        )

    updated_user = await repository.update_instance(
        id=user_id, data=data, session=session
    )
    return updated_user
