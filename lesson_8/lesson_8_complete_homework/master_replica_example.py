import asyncio
import redis
import redis.asyncio

MASTER_HOST = "127.0.0.1"
MASTER_PORT = 6379

REPLICA_HOST = "127.0.0.1"
REPLICA_PORT = 6380

async def main():
    master = redis.asyncio.Redis(host=MASTER_HOST, port=MASTER_PORT, decode_responses=True)
    replica = redis.asyncio.Redis(host=REPLICA_HOST, port=REPLICA_PORT, decode_responses=True)

    await master.set("mykey", "myvalue")
    print("Write to master")

    val = await replica.get('mykey')
    print(f"Read from replica value - {val}")

    await master.aclose()
    await replica.aclose()

if __name__ == '__main__':
    asyncio.run(main())