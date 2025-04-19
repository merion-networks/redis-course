import asyncio
import redis.asyncio as aioredis
import json

QUEUE_NAME = "tasks:list:queue"

r = aioredis.Redis()

async def main():
    for user_id, order_id in [
        (33, 12345),
        (44, 12346),
        (55, 12347)
    ]:
        msg = json.dumps({"user_id": user_id, "order_id": order_id})
        await r.rpush(QUEUE_NAME, msg)

if __name__ == "__main__":
    asyncio.run(main())