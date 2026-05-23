import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from loguru import logger

from app.services.sse_manager import sse_manager

router = APIRouter()


@router.get("/sse")
async def sse_stream(request: Request):
    queue = await sse_manager.subscribe()
    sid = sse_manager._counter

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    yield f": keepalive\n\n"
        finally:
            await sse_manager.unsubscribe(sid)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
