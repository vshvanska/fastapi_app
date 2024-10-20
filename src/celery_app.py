from celery import Celery
from src.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


celery_app.conf.update(
    result_expires=3600, timezone="UTC", enable_utc=True, imports=["src.comments.tasks"]
)
