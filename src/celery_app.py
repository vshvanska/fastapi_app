from celery import Celery
from src.config import settings

celery_app = Celery(
    "worker",
    broker=settings.celery.CELERY_BROKER_URL,
    backend=settings.celery.CELERY_RESULT_BACKEND,
)


celery_app.conf.update(
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    task_always_eager=True,
    task_eager_propagates=True,
    imports=["src.comments.tasks", "src.posts.tasks"],
)
