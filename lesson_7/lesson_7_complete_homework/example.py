import redis.asyncio as aioredis
import asyncio

async def main():
    client = aioredis.Redis(decode_responses=True)

    pipe = client.pipeline(transaction=True)
    pipe.set("y", 10)
    pipe.decr("y")
    results = await pipe.execute()  # MULTI/EXEC
    print(results)

    await client.aclose()

asyncio.run(main())
