from fastapi import APIRouter
from fastapi import Depends
from src.auth.repositories import UserRepository
from src.auth.schemas import UserCreate
from src.dependencies import get_user_repository, get_async_session

user_router = APIRouter(tags=["Users"], prefix="/users")


@user_router.post("/", name="users:register-user")
async def register_user(
        user: UserCreate,
        repository: UserRepository = Depends(get_user_repository),
        session=Depends(get_async_session)):
    return await repository.create_instance(data=user, session=session)
