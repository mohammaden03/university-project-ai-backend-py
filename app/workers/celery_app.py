from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "makhtootat_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.ocr_tasks",
        "app.workers.embedding_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 min max for large manuscripts
    worker_prefetch_multiplier=1,
)
