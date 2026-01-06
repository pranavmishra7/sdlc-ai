from .base import BaseStore

_MEMORY = {}

class MemoryStore(BaseStore):
    def save(self, job_id: str, data: dict):
        _MEMORY[job_id] = data

    def load(self, job_id: str) -> dict:
        return _MEMORY.get(job_id)
