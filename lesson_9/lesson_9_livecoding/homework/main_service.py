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
    ...
    # END
