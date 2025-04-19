import redis.asyncio as aioredis
from fastapi import FastAPI

app = FastAPI()
r = aioredis.Redis(decode_responses=True)
orders_data = {}  # простая имитация БД

@app.post("/orders/create")
async def create_order(user_id: int):
    """
    Создаём "заказ", записываем user_id в условную in-memory БД,
    публикуем 3 события (cheque, warehouse, notify) в 3 разных Streams.
    """
    # BEGIN YOUR SOLUTION HERE
    order_id = len(orders_data) + 1
    orders_data[order_id] = {
        "user_id": user_id,
        "status": "CREATED",
    }

    message = {
        "order_id": str(order_id),
        "user_id": str(user_id),
    }

    await r.xadd("stream:cheque", message)
    await r.xadd("stream:warehouse", message)
    await r.xadd("stream:notify", message)

    return {
        "order_id": str(order_id),
        "detail": "Tasks queued in Streams."
    }
    # END

