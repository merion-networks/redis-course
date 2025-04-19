import asyncio
import redis.asyncio as aioredis

QUEUE_NAME = "tasks:list"

async def main():
    await asyncio.sleep(3)
    r = aioredis.Redis(decode_responses=True)
    print("Consumer strarted, listning...")
    while True:
        result = await r.blpop(QUEUE_NAME, timeout=0)
        task_value = result[1]
        print("Got task:", task_value)
        await asyncio.sleep(1)

    await r.aclose()


if __name__ == "__main__":
    asyncio.run(main())