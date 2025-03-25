# BEGIN YOUR SOLUTION HERE
from app.redis_client import redis_client


# 1. Lua-скрипт: атомарное обновление статистики при просмотре поста.
async def update_post_view_atomic(post_id: int, user_id: str, history_limit: int, lua_sha: str):
    """
    Вызывает Lua-скрипт (через EVALSHA) для атомарного обновления статистики просмотра поста.
    """
    result = await redis_client.redis.evalsha(
        lua_sha,
        0,
        str(post_id),
        user_id,
        str(history_limit)
    )
    return result


# 2. Пайплайн: массовые лайки.
async def bulk_like_operations(operations: list[dict]):
    """
    Выполняет массовые операции лайков (операции вида
       {"post_id": 1, "user_id": "2", "author_id": 10})
    через Redis-пайплайн:
      - SADD likes:{post_id} user_id
      - ZINCRBY author:rating 1 author_id
    """
    pipe = redis_client.redis.pipeline(transaction=True)
    for op in operations:
        pipe.sadd(f"likes:{op['post_id']}", op['user_id'])
        pipe.zincrby("author:rating", 1, op['author_id'])
    results = await pipe.execute()
    return results
# END