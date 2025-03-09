import redis.asyncio as aioredis
import asyncio

client = aioredis.Redis(decode_responses=True)

async def find_keys(pattern: str):
    all_keys = await client.keys(pattern)
    return all_keys


async def scan_keys_plain(pattern: str, count: int = 100):
    cursor = 0
    while True:
        cursor, keys = await client.scan(
            cursor=cursor,
            match=pattern,
            count=count
        )
        for key in keys:
            print("Found key:", key)
        if cursor == 0:
            break

async def scan_keys_iter(pattern: str, count: int = 100):
    # вариант с scan_iter — упрощённая итерация
    async for key in client.scan_iter(match=pattern, count=count):
        print("Found key:", key)

async def sscan_all(key: str, pattern: str = None):
    cursor = 0
    members = []
    while True:
        if pattern:
            search_pattern = pattern
        else:
            search_pattern = '*'
        cursor, batch = await client.sscan(
            key, cursor, match=search_pattern, count=10
        )
        members.extend(batch)
        if cursor == 0:
            break
    endphrase = f' by pattern {pattern}' if pattern else ''
    for member in members:
        print(f'Member of set {key} - {member}' + endphrase)


async def sscan_all_iter(key: str, pattern: str = "*"):    
    # sscan_iter — итератор по элементам множества
    async for member in client.sscan_iter(key, match=pattern, count=10):
        print("Found member:", member)

async def hscan_all(key: str, pattern: str = None):
    cursor = 0
    members = {}
    while True:
        if pattern:
            search_pattern = pattern
        else:
            search_pattern = '*'
        cursor, batch = await client.hscan(
            key, cursor, match=search_pattern, count=10
        )
        members.update(batch)
        if cursor == 0:
            break
    endphrase = f' by pattern {pattern}' if pattern else ''
    for member, value in members.items():
        print(f'Member of set {key} - {member}:{value}' + endphrase)

async def hscan_all_iter(key: str, pattern: str = "*"):    
    # sscan_iter — итератор по элементам хэша
    async for member in client.hscan_iter(key, match=pattern, count=10):
        print("Found member:", member)

async def zscan_all(key: str, pattern: str = None):
    cursor = 0
    members = {}
    while True:
        if pattern:
            search_pattern = pattern
        else:
            search_pattern = '*'
        cursor, batch = await client.zscan(
            key, cursor, match=search_pattern, count=10
        )
        members.update(batch)
        if cursor == 0:
            break
    endphrase = f' by pattern {pattern}' if pattern else ''
    for member, score in members.items():
        print(f'Member of set {key} - {member} with score {score}' + endphrase)

async def zscan_all_iter(key: str, pattern: str = "*"):    
    # sscan_iter — итератор по элементам хэша
    async for member in client.zscan_iter(key, match=pattern, count=10):
        print("Found member:", member)

asyncio.run(zscan_all_iter("post:views:ranking"))

