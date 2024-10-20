from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_async_session, get_comment_repository
from src.repositories import AbstractRepository

analytics_router = APIRouter(tags=["Analytics"], prefix="/analytics")


@analytics_router.get("/comments-daily-breakdown")
async def get_comments(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    repository: AbstractRepository = Depends(get_comment_repository),
    session: AsyncSession = Depends(get_async_session),
):
    comments = await repository.get_analytics(
        session=session, date_from=date_from, date_to=date_to
    )
    return comments
