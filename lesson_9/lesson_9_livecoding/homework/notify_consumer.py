import asyncio
import redis.asyncio as aioredis

STREAM_KEY = "stream:notify"
GROUP_NAME = "group_notify"
CONSUMER_NAME = "notify_worker"

async def main():
    # BEGIN YOUR SOLUTION HERE
    ...
    # END

if __name__ == "__main__":
    asyncio.run(main())
