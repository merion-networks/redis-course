import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException

app = FastAPI()
redis_client = aioredis.Redis(host="localhost", port=6379, decode_responses=True)

# Пусть ключ "leaderboard" будет содержать наш рейтинг
LEADERBOARD_KEY = "leaderboard"


@app.post("/leaderboard/add")
async def add_or_update_score(item_id: str, score: float):
    """
    Устанавливает score для item_id (если item уже в ZSET, обновит).
    """
    # ZADD leaderboard score item_id
    result = await redis_client.zadd(LEADERBOARD_KEY, {item_id: score})
    # zadd возвращает количество новых элементов (которые раньше не было),
    # если item_id уже существовал - score обновится, а result будет 0.
    return {
        "result": f"{'Inserted' if result else 'Updated'} score for {item_id}",
        "score": score,
    }


@app.post("/leaderboard/increment")
async def increment_score(item_id: str, increment: float = 1.0):
    """
    Увеличивает score для item_id на increment (по умолчанию +1).
    ZINCRBY leaderboard increment item_id
    """
    new_score = await redis_client.zincrby(LEADERBOARD_KEY, increment, item_id)
    return {"item_id": item_id, "new_score": new_score}


@app.get("/leaderboard/top")
async def get_top_n(n: int = 10):
    """
    Получаем TOP-n (score по убыванию).
    ZREVRANGE leaderboard 0 n-1 WITHSCORES
    """
    top_members = await redis_client.zrevrange(
        LEADERBOARD_KEY, 0, n - 1, withscores=True
    )
    # В redis.asyncio, если withscores=True, возвращается список кортежей [(member, score), ...]
    return {
        "leaderboard": [
            {"item_id": member, "score": score} for (member, score) in top_members
        ]
    }


@app.get("/leaderboard/rank")
async def get_rank(item_id: str):
    """
    Узнаём позицию (ранг) элемента item_id (чем меньше индекс, тем выше в списке).
    ZREVRANK вернёт индекс в обратном порядке, то есть 0 = 1 место.
    """
    # score = await redis_client.zscore(LEADERBOARD_KEY, item_id) чтобы вернуть вес
    rank = await redis_client.zrevrank(LEADERBOARD_KEY, item_id)
    if rank is None:
        raise HTTPException(status_code=404, detail="Item not in leaderboard")
    return {"item_id": item_id, "rank": rank + 1}  # rank=0 => 1-е место


@app.delete("/leaderboard/remove")
async def remove_item(item_id: str):
    removed = await redis_client.zrem(LEADERBOARD_KEY, item_id)
    return {"removed": bool(removed)}


@app.delete("/leaderboard/trim")
async def trim_leaderboard(keep: int = 100):
    """
    Оставляем только топ-keep.
    Удаляем всех с индексом > keep-1 (т.е. 100, 101...).
    """
    removed_count = await redis_client.zremrangebyrank(LEADERBOARD_KEY, keep, -1)
    return {"removed_count": removed_count}


@app.delete("/leaderboard/trim")
async def trim_leaderboard(keep: int = 100):
    """
    Оставляем в лидере только первые keep участников.
    Удаляем всех с индексом > keep-1.
    """
    removed_count = await redis_client.zremrangebyrank(LEADERBOARD_KEY, keep, -1)
    return {"removed_count": removed_count}
