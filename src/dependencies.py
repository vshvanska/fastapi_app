from src.auth.repositories import UserRepository
from src.database import SessionLocal
from src.repositories import AbstractRepository


def get_user_repository() -> AbstractRepository:
    return UserRepository()


async def get_async_session():
    async with SessionLocal() as session:
        yield session
