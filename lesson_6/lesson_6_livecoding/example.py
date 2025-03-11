import asyncio
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

redis_client = aioredis.Redis(decode_responses=True)
app = FastAPI()

@app.post("/publish")
async def publish_message(channel: str, message: str):
    num_subscribers = await redis_client.publish(channel, message)
    return {"channel": channel, "message": message, "notified": num_subscribers}

async def event_generator(channel: str):
    """
    Отправляет уведомления, как только они поступают из Redis.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message.get("data")
                yield f"data: {data}\n\n"
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        raise

@app.get("/subscribe/")
async def subscribe(channel: str):
    """
    Эндпоинт для подписки на уведомления о новых сообщениях.
    Клиент получает данные через Server-Sent Events (SSE).
    """
    return StreamingResponse(event_generator(channel), media_type="text/event-stream")
