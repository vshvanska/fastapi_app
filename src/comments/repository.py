from datetime import date
from http.client import HTTPException
from sqlalchemy import select, func, case
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

    async def get_analytics(
        self, session: AsyncSession, date_from: date = None, date_to: date = None
    ):
        stmt = select(
            func.count(Comment.id).label("total_comments"),
            func.sum(case((Comment.is_active == True, 1), else_=0)).label(
                "active_comments"
            ),
            func.sum(case((Comment.is_active == False, 1), else_=0)).label(
                "blocked_comments"
            ),
        )
        if date_from:
            stmt = stmt.where(Comment.created_at >= date_from)

        if date_to:
            stmt = stmt.where(Comment.created_at <= date_to)

        result = await session.execute(stmt)
        comments_stats = result.mappings().one_or_none()

        return comments_stats
