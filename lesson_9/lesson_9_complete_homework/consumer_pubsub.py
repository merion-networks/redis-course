import asyncio
import redis.asyncio as aioredis

CHANNEL_NAME = "news:channel"
r = aioredis.Redis(decode_responses=True)

async def main():
    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            print(f"Got: {message.get("data")}")
        await asyncio.sleep(1)
    await pubsub.unsubscribe(CHANNEL_NAME)

if __name__ == "__main__":
    asyncio.run(main())