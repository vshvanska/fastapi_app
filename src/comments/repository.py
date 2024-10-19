from http.client import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.comments.models import Comment


class CommentRepository:
    model = Comment

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
        self, session: AsyncSession, post_id: int = None, user_id: int = None
    ):
        result = (
            select(self.model)
            .options(selectinload(Comment.user))
            .options(selectinload(Comment.post))
        )
        if user_id:
            result = result.where(self.model.user_id == user_id)
        if post_id:
            result = result.where(self.model.post_id == post_id)

        result = await session.scalars(result)

        return result.all()

    async def delete_instance(self, id: int, session: AsyncSession):
        comment = await self.get_instance(id, session)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        await session.delete(comment)
        await session.commit()
