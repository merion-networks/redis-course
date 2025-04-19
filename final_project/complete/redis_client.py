import redis.asyncio as redis

redis_client = redis.Redis(decode_responses=True)
