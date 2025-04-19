import asyncio
import redis.asyncio as aioredis
import redis
import redis.exceptions

STREAM_KEY = "tasks:stream"
GROUP_NAME = "groupA"
CONSUMER_NAME = "worker1"
r = aioredis.Redis(decode_responses=True)

async def main():
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        print("Group created:", GROUP_NAME)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Group already exists!")
        else:
            raise e
        
    print(f"Consumer {CONSUMER_NAME} listening in group {GROUP_NAME}...")

    while True:
        messages = await r.xreadgroup(
            groupname=GROUP_NAME,
            consumername=CONSUMER_NAME,
            streams={STREAM_KEY: ">"},
            count=10,
            block=5000
        )
        if messages:
            for (stream, msg_list) in messages:
                for msg_id, fields in msg_list:
                    print(f"[{CONSUMER_NAME}] Recieved: {msg_id} => {fields}")
                    await asyncio.sleep(1)
                    await r.xack(STREAM_KEY, GROUP_NAME, msg_id)
                    print(f"[{CONSUMER_NAME}] XACK {msg_id}")

if __name__ == "__main__":
    asyncio.run(main())