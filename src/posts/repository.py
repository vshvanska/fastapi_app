from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.auth.models import User
from src.posts.models import Post
from src.repositories import DBRepository


class PostRepository(DBRepository):
    model = Post

    async def create_instance(self, data, session):
        new_item = self.model(**data)
        session.add(new_item)
        await session.commit()
        return new_item

    async def get_list(
        self,
        session,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        title: Optional[str] = None,
    ):
        result = select(self.model).options(selectinload(self.model.user))
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

    async def make_instance_inactive(self, id: int, session: AsyncSession):
        post = await self.get_instance(id, session)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        post.is_active = False
        session.add(post)
        await session.commit()
        return post
