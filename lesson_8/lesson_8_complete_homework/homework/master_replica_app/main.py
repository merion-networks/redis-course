from fastapi import FastAPI
from redis.sentinel import Sentinel

app = FastAPI()

# Параметры Sentinel и название мастера
SENTINEL_HOST = "127.0.0.1"
SENTINEL_PORT = 26379
MASTER_NAME = "mymaster"

# Инициализируем Sentinel
sentinel = Sentinel([(SENTINEL_HOST, SENTINEL_PORT)], socket_timeout=1)

# Получаем коннект к мастеру и к реплике
master = sentinel.master_for(MASTER_NAME, socket_timeout=1, db=0)
replica = sentinel.slave_for(MASTER_NAME, socket_timeout=1, db=0)

@app.post("/set")
def set_value(key: str, value: str):
    # Запись всегда идет в мастер
    master.set(key, value)
    return {"status": "ok", "written_key": key, "value": value}

@app.get("/get")
def get_value(key: str):
    # Чтение идет с реплики
    val = replica.get(key)
    return {"key": key, "value": val.decode() if val else None}
