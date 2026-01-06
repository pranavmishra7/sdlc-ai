# import json
# import redis
# from app.config.settings import settings
# from .base import BaseStore

# class RedisStore(BaseStore):
#     def __init__(self):
#         self.client = redis.Redis.from_url(settings.REDIS_URL)

#     def save(self, job_id: str, data: dict):
#         self.client.set(job_id, json.dumps(data))

#     def load(self, job_id: str) -> dict | None:
#         raw = self.client.get(job_id)
#         return json.loads(raw) if raw else None
