import asyncio
import redis.asyncio as aioredis

STREAM_KEY = "stream:cheque"
GROUP_NAME = "group_cheque"
CONSUMER_NAME = "cheque_worker"

async def main():
    # BEGIN YOUR SOLUTION HERE
    ...
    # END

if __name__ == "__main__":
    asyncio.run(main())
