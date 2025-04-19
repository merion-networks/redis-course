import asyncio
import redis.asyncio as aioredis

STREAM_KEY = "stream:warehouse"
GROUP_NAME = "group_warehouse"
CONSUMER_NAME = "warehouse_worker"

async def main():
    # BEGIN YOUR SOLUTION HERE
    ...
    # END


if __name__ == "__main__":
    asyncio.run(main())
