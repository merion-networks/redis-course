import asyncio
import redis.asyncio as aioredis
import redis

STREAM_KEY = "stream:cheque"
GROUP_NAME = "group_cheque"
CONSUMER_NAME = "cheque_worker"

async def main():
    r = aioredis.Redis(decode_responses=True)
    # BEGIN YOUR SOLUTION HERE
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        print("Group created:", GROUP_NAME)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Group already exists!")
        else:
            raise e
    
    print("[cheque] service started? waiting for tasks...")

    while True:
        resp = await r.xreadgroup(
            groupname=GROUP_NAME,
            consumername=CONSUMER_NAME,
            streams={STREAM_KEY: ">"},
            count=1,
            block=5000
        )
        if not resp:
            continue

        for (_, msgs) in resp:
            for msg_id, fields in msgs:
                print(f"[cheque] Got {msg_id} => {fields}")
                await asyncio.sleep(1)
                await r.xack(STREAM_KEY, GROUP_NAME, msg_id)
                print(f"[cheque] ACK {msg_id}")
    # END


if __name__ == "__main__":
    asyncio.run(main())
