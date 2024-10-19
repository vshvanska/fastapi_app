from src.auth.auth import Authenticator
from src.auth.repositories import UserRepository
from src.database import SessionLocal
from src.posts.repository import PostRepository
from src.repositories import AbstractRepository


def get_user_repository() -> AbstractRepository:
    return UserRepository()


def get_post_repository() -> AbstractRepository:
    return PostRepository()


def get_authenticator() -> Authenticator:
    return Authenticator()


async def get_async_session():
    async with SessionLocal() as session:
        yield session
