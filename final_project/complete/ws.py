import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis_client import redis_client

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("room:general")

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        await pubsub.unsubscribe("room:general")
