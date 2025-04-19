import asyncio
import redis.asyncio as aioredis
import json

QUEUE_NAME = "tasks:list:queue"
FALLBACK_NAME = "tasks:list:fallback"

r = aioredis.Redis()

async def process_message(msg: str):
    data = json.loads(msg)
    print(f"Processing order {data.get("order_id")} for user {data.get("user_id")}")
    if data.get("order_id") % 2 == 0:
        raise Exception("Simulated failure")

async def worker():
    print("Worker started!")
    while True:
        result = await r.blmove(QUEUE_NAME, FALLBACK_NAME, 5, "LEFT", "RIGHT")
        if result:
            print("Got message:", result)
            try:
                await process_message(result)
                await r.lrem(FALLBACK_NAME, 1, result)
                print("Succesfully processed and removed from fallback")
            except Exception as e:
                print(f"Error: {e}")
                print("Message left in fallback for retry")
            

if __name__ == "__main__":
    asyncio.run(worker())