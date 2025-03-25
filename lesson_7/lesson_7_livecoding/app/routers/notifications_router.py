# BEGIN YOUR SOLUTION HERE
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.redis_client import redis_client

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)

async def event_generator(author_id: int):
    """
    Генератор событий, подписывающийся на канал "new_post:{author_id}".
    Отправляет уведомления, как только они поступают из Redis.
    """
    pubsub = redis_client.redis.pubsub()
    channel_name = f"new_post:{author_id}"
    await pubsub.subscribe(channel_name)
    try:
        while True:
            # Получаем сообщение с канала; timeout позволяет периодически проверять завершение
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                data = message["data"]
                # Если данные закодированы в байты, декодируем
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                yield f"data: {data}\n\n"
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        # При отмене генератора отписываемся от канала
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
        raise

@router.get("/subscribe/{author_id}")
async def subscribe_new_post(author_id: int):
    """
    Эндпоинт для подписки на уведомления о новых постах от автора.
    Клиент получает данные через Server-Sent Events (SSE).
    """
    return StreamingResponse(event_generator(author_id), media_type="text/event-stream")
# END