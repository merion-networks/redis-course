import redis.asyncio as aioredis
from fastapi import FastAPI

app = FastAPI()
redis_client = aioredis.Redis(host="localhost", port=6379, decode_responses=True)

QUEUE_KEY = "tasks"

# СПИСКИ


@app.post("/enqueue")
async def enqueue_task(task: str):
    """
    Добавляем новую задачу в очередь (в конец списка).
    Пример запроса:
      POST /enqueue?task=do_something
    """
    # RPUSH добавляет элемент в конец списка
    await redis_client.rpush(QUEUE_KEY, task)
    return {"status": "added", "task": task}


@app.post("/dequeue")
async def dequeue_task():
    """
    Извлекаем задачу из начала списка (FIFO).
    Если очередь пустая, возвращаем None.
    """
    # LPOP извлекает и возвращает первый элемент
    task = await redis_client.lpop(QUEUE_KEY)
    return {"task": task}


@app.get("/queue")
async def show_queue():
    """
    Возвращает все задачи в очереди (от 0-го до -1 индекса).
    """
    tasks = await redis_client.lrange(QUEUE_KEY, 0, -1)
    return {"queue": tasks}


@app.post("/stack/push")
async def stack_push(item: str):
    # LPUSH -> вставляем в начало
    await redis_client.lpush("stack", item)
    return {"status": "pushed", "item": item}


@app.post("/stack/pop")
async def stack_pop():
    # LPOP -> достаём с начала
    item = await redis_client.lpop("stack")
    return {"item": item}


# МНОЖЕСТВА


@app.post("/sets/add")
async def add_to_set(set_name: str, item: str):
    """
    Добавляет элемент в множество set_name.
    Если элемент уже есть, Redis ничего не изменит.
    """
    # SADD key member...
    await redis_client.sadd(set_name, item)
    return {"status": "added (or already existed)", "item": item}


@app.get("/sets/{set_name}/members")
async def get_set_members(set_name: str):
    """
    Возвращает все элементы множества set_name.
    """
    # SMEMBERS key
    members = await redis_client.smembers(set_name)
    return {"members": members}


@app.get("/sets/{set_name}/check")
async def check_member(set_name: str, item: str):
    """
    Проверяет, содержится ли 'item' в множестве set_name.
    Возвращает True/False.
    """
    # SISMEMBER key member
    is_member = await redis_client.sismember(set_name, item)
    return {"exists": bool(is_member)}


@app.delete("/sets/{set_name}")
async def remove_from_set(set_name: str, item: str):
    """
    Удаляет элемент из множества. Если элемента не было — ничего не происходит.
    """
    # SREM key member
    count = await redis_client.srem(set_name, item)
    return {"removed": bool(count), "item": item}


@app.get("/sets/{set_name}/size")
async def get_set_size(set_name: str):
    """
    Возвращает количество элементов в множестве.
    """
    # SCARD key
    size = await redis_client.scard(set_name)
    return {"size": size}


@app.get("/sets/common")
async def get_common(key1: str, key2: str):
    """
    Находим пересечение двух множеств
    """
    # SINTER key1 key2
    common_values = await redis_client.sinter(key1, key2)
    return {"common_tags": list(common_values)}


@app.get("/union")
async def get_union(key1: str, key2: str):
    """
    Находим объединение двух множеств.
    Аналог команды SUNION key1 key2.
    """
    union_values = await redis_client.redis.sunion(key1, key2)
    return {"union": list(union_values)}


@app.get("/diff")
async def get_difference(key1: str, key2: str):
    """
    Находим разность множеств: элементы, которые есть в key1, но отсутствуют в key2.
    Аналог команды SDIFF key1 key2.
    """
    diff_values = await redis_client.redis.sdiff(key1, key2)
    return {"difference": list(diff_values)}
