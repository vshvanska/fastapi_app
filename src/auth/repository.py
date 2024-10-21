from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.hasher import hasher
from src.auth.models import User
from src.repositories import DBRepository


class UserRepository(DBRepository):
    model = User

    async def get_list(self, session, *args, **kwargs):
        result = await session.scalars(select(self.model))
        return result.all()

    async def create_instance(self, data, session: AsyncSession):
        data = await self.process_data(data)

        await self.check_if_user_exists(data, session)

        new_item = self.model(**data)
        session.add(new_item)
        await session.commit()
        return JSONResponse(
            content={"message": "User created successfully", "user_id": new_item.id},
            status_code=201,
        )

    async def check_if_user_exists(self, data, session):
        instance = await self.get_by_email(data["email"], session)
        if instance:
            raise HTTPException(status_code=400, detail="Email already registered")

        instance = await self.get_by_username(data["username"], session)
        if instance:
            raise HTTPException(
                status_code=400, detail="User with this username already registred"
            )

    async def get_by_email(self, email, session):
        result = await session.scalars(
            select(self.model).where(self.model.email == email)
        )
        return result.one_or_none()

    async def get_by_username(self, username, session):
        result = await session.scalars(
            select(self.model).where(self.model.username == username)
        )
        return result.one_or_none()

    async def process_data(self, data):
        data = data.model_dump()

        data["hashed_password"] = await hasher.hash(data["password"])
        del data["password_confirm"]
        del data["password"]

        data["email"] = data["email"].lower()

        return data
