import os
from celery import Celery

# -------------------------------------------------
# Celery Configuration
# -------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "sdlc_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# -------------------------------------------------
# Celery Settings
# -------------------------------------------------

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

# -------------------------------------------------
# Auto-discover Tasks
# -------------------------------------------------

celery_app.autodiscover_tasks([
    "app.workers"
])
