from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.auth.models import User
from src.posts.models import Post


class PostRepository:
    model = Post

    async def create_instance(self, data: dict, session: AsyncSession):
        new_item = self.model(**data)
        session.add(new_item)
        await session.commit()
        return new_item

    async def update_instance(self, id: int, data: dict, session: AsyncSession):
        data = data.model_dump()
        post = await self.get_instance(id, session)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        for key, value in data.items():
            setattr(post, key, value)

        session.add(post)
        await session.commit()

        return post

    async def get_instance(self, id: int, session: AsyncSession):
        result = await session.scalars(select(self.model).where(self.model.id == id))
        return result.one_or_none()

    async def get_list(
        self,
        session: AsyncSession,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        title: Optional[str] = None,
    ):
        result = select(self.model).options(selectinload(Post.user))
        if user_id:
            result = result.where(self.model.user_id == user_id)
        if username:
            result = result.join(self.model.user).where(
                User.username.ilike(f"%{username}%")
            )
        if title:
            result = result.where(self.model.title.ilike(f"%{title}%"))
        result = await session.scalars(result)
        return result.all()

    async def delete_instance(self, id: int, session: AsyncSession):
        post = await self.get_instance(id, session)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        await session.delete(post)
        await session.commit()
