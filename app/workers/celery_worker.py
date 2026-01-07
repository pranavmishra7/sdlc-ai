from celery import Celery

celery_app = Celery(
    "sdlc_ai",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# 🔴 CRITICAL: import tasks so Celery can register them
import app.workers.tasks  # noqa
