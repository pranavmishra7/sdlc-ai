import asyncio
from typing import Dict, List, Any


class SSEManager:
    """
    Simple in-memory SSE event manager.
    One channel per job_id.
    """

    def __init__(self):
        self._queues: Dict[str, List[asyncio.Queue]] = {}

    def register(self, job_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._queues.setdefault(job_id, []).append(queue)
        return queue

    def unregister(self, job_id: str, queue: asyncio.Queue):
        if job_id in self._queues:
            self._queues[job_id].remove(queue)
            if not self._queues[job_id]:
                del self._queues[job_id]

    async def publish(self, job_id: str, event: Dict[str, Any]):
        queues = self._queues.get(job_id, [])
        for queue in queues:
            await queue.put(event)


# Singleton instance
sse_manager = SSEManager()
