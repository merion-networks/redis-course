import asyncio
import redis.asyncio as aioredis

STREAM_KEY = "tasks:stream"
GROUP_NAME = "groupA"
CONSUMER_NAME = "worker1"
r = aioredis.Redis(decode_responses=True)

async def main():
    for i in range(5):
        fields = {"task_id": str(i), "info": f"Task_{i}"}
        msg_id = await r.xadd(STREAM_KEY, fields=fields)
        print("XADD =>", msg_id, fields)
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
