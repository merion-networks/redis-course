# BEGIN YOUR SOLUTION HERE
from fastapi import APIRouter, Query, HTTPException
import time
from app.redis_client import redis_client


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/redis-keys")
async def search_redis_keys(
    pattern: str = Query(..., description="Шаблон поиска ключей, например: post:*"),
    method: str = Query("scan", description="Метод поиска: 'keys' или 'scan'")
):
    """
    Эндпоинт для поиска ключей в Redis.
    
    При использовании метода 'keys' выпаолняется команда KEYS, которая сразу возвращает все совпадающие ключи .
    При использовании метода 'scan' итеративно перебираются ключи с использованием SCAN,
    что позволяет избежать блокировки Redis при большом количестве ключей .
    
    Возвращается список найденных ключей, время выполнения, а для SCAN- количество итераций.
    """
    if method == "keys":
        start = time.time()
        keys = await redis_client.redis.keys(pattern)
        elapsed = time.time() - start
        return {
            "method": "keys",
            "keys": keys,
            "elapsed_time": elapsed,
            "note": "Команда KEYS возвращпает все ключи сразу , что может блокировать Redis при большом количестве ключей."
        }        
    elif method == "scan":
        start = time.time()
        iterations, keys = await get_all_keys(pattern=pattern)
        elapsed = time.time() - start
        return {
            "method": "keys",
            "keys": keys,
            "iterations": iterations,
            "elapsed_time": elapsed,
            "note": "Команда SCAN Команда SCAN итеративна и не блокирует Redis, поэтому предпочтительна в продакшене."
        }   
        
    else:
        raise HTTPException(status_code=400, detail="Invalid method. Use 'keys' or 'scan'.")

async def get_all_keys(pattern: str) -> list:
    """
    Итеративно получает все ключи,  удовлетворяющие заданному шаблону,
    с использованием команды SCAN .
    """
    keys = []
    cursor = 0
    iterations = 0
    while True:
        cursor, partial_keys = await redis_client.redis.scan(cursor=cursor, match=pattern, count=10)
        keys.extend(partial_keys)
        iterations += 1
        if cursor == 0:
            break
    return iterations, keys
    

@router.post("/cleanup-cached-posts")
async def cleanup_cached_posts(limit: int = 5):
    """
    Эндпоинт для очистки кэша постов.
    
    Если в кэше Redis (ключи вида 'post:*') находится больше чем `limit` постов,
    удаляются все ключи, кроме первых `limit` (при этом ключи сортируются лексико графически).
    
    Возвращается информация о том , сколько ключей удалено и сколько оставлено.
    """
    _, keys = await get_all_keys("post:*")
    total = len(keys)
    if total <= limit:
        return {"detail": f"Cleanup not required, total keys: {total}"}
    # Для примера сортируем ключи лексикографически (в реальном приложении можно хранить timestamp)
    keys.sort()
    # Оставляем первые `limit` ключей, остальные удаляем
    keys_to_remove = keys[limit:]
    for key in keys_to_remove:
        if ":ranking" in key:
            continue
        await redis_client.redis.delete(key)
    return {
        "detail": f"Removed {len(keys_to_remove)} keys stayed {limit} keys. Before clean {total}"
    }

# END