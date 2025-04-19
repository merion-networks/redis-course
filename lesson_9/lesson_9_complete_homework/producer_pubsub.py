import asyncio
import redis.asyncio as aioredis

CHANNEL_NAME = "news:channel"
r = aioredis.Redis(decode_responses=True)

async def main():
    print("Publisher started. Type message to publish. Ctrl + C for exit.")
    while True:
        try:
            line = input("Message\n>>>")
        except EOFError:
            break
        if not line:
            continue
        num_subs = await r.publish(CHANNEL_NAME, line)
        print(f"Published to {CHANNEL_NAME}, subs = {num_subs}")

if __name__ == "__main__":
    asyncio.run(main())