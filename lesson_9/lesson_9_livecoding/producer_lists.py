import asyncio
import redis.asyncio as aioredis

QUEUE_NAME = "tasks:list"

async def main():
    r = aioredis.Redis(decode_responses=True)
    for i in range(5):
        task_data = f"task_{i}"
        await r.rpush(QUEUE_NAME, task_data)
        print("Enqueued:", task_data)
    await r.aclose()

if __name__ == "__main__":
    asyncio.run(main())