import asyncio

from celery import shared_task
from src.comments.repository import CommentRepository
from src.dependencies import get_async_session


@shared_task
def create_reply_comment(data: dict):
    asyncio.run(create_comment_task(data))


async def create_comment_task(data):
    async for session in get_async_session():
        repository = CommentRepository()
        item = await repository.create_instance(data=data, session=session)
        return item.__dict__
