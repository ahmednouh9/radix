import asyncio
import json
from typing import Dict, Any
from loguru import logger


class SSEManager:
    def __init__(self):
        self._queues: Dict[int, asyncio.Queue] = {}
        self._counter = 0

    def _cleanup(self):
        disconnected = []
        for sid, queue in self._queues.items():
            if queue._finished:
                disconnected.append(sid)
        for sid in disconnected:
            del self._queues[sid]
            logger.debug(f"Cleaned up disconnected SSE client {sid}")

    async def subscribe(self) -> asyncio.Queue:
        self._counter += 1
        sid = self._counter
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._queues[sid] = queue
        logger.info(f"SSE client {sid} connected (total: {len(self._queues)})")
        return queue

    async def unsubscribe(self, sid: int):
        if sid in self._queues:
            del self._queues[sid]
            logger.info(f"SSE client {sid} disconnected (remaining: {len(self._queues)})")

    async def broadcast(self, event_data: Dict[str, Any]):
        self._cleanup()
        message = json.dumps(event_data, default=str)
        disconnected = []
        for sid, queue in self._queues.items():
            try:
                await asyncio.wait_for(queue.put(message), timeout=1.0)
            except asyncio.TimeoutError:
                disconnected.append(sid)
            except Exception as e:
                logger.error(f"Error sending to SSE client {sid}: {e}")
                disconnected.append(sid)
        for sid in disconnected:
            await self.unsubscribe(sid)


sse_manager = SSEManager()
