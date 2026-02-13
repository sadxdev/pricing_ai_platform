from celery import Celery
from app.core.config import settings

celery = Celery(
    "pricing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.task_routes = {
    "app.workers.*": {"queue": "celery"}
}

celery.autodiscover_tasks(["app.workers"])