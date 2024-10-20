import asyncio
import json

from src.celery_app import celery_app
from src.dependencies import get_async_session
from src.genai import make_request_to_model
from src.posts.repository import PostRepository


@celery_app.task
def check_post(data: dict):
    asyncio.create_task(process_comment(data))


async def process_comment(data):
    response = json.loads(make_request_to_model(data["content"]))
    if response.get("contain_bad_words"):
        async for session in get_async_session():
            repository = PostRepository()
            await repository.make_instance_inactive(id=data["id"], session=session)
