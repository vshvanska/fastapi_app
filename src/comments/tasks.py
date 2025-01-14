import asyncio
import json

from src.celery_app import celery_app
from src.comments.repository import CommentRepository
from src.dependencies import get_async_session
from src.genai import make_request_to_model


@celery_app.task
def create_reply_comment(data: dict):
    asyncio.create_task(create_comment(data))


@celery_app.task
def check_comment(data: dict):
    asyncio.create_task(process_comment(data))


async def create_comment(data):
    async for session in get_async_session():
        repository = CommentRepository()
        item = await repository.create_instance(data=data, session=session)
        return item.__dict__


async def process_comment(data):
    response = json.loads(make_request_to_model(data["content"]))
    if response.get("contain_bad_words"):
        async for session in get_async_session():
            repository = CommentRepository()
            await repository.make_instance_inactive(id=data["id"], session=session)
