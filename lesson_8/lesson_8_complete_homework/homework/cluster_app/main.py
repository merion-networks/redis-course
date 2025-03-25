import uvicorn
from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from redis.asyncio.cluster import RedisCluster, ClusterNode

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    При запуске приложения инициализируем клиента RedisCluster,
    подключаясь к 3 мастер-нодам (и их репликам).
    """

    startup_nodes = [
        ClusterNode("127.0.0.1", 7000),
        ClusterNode("127.0.0.1", 7001),
        ClusterNode("127.0.0.1", 7002),
    ]

    cluster_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
    app.state.redis = cluster_client
    yield

    await cluster_client.aclose()

app = FastAPI(
    title="Redis Cluster Demo (3 masters, 2 replicas each)",
    lifespan=lifespan
)

@app.post("/set", summary="Запись ключа в Redis Cluster")
async def set_value(
    key: str = Query(..., description="Ключ"),
    value: str = Query(..., description="Значение")
):
    """
    Записывает ключ-значение в кластер Redis.
    """
    try:
        await app.state.redis.set(key, value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"detail": f"Key '{key}' set to '{value}' in cluster."}

@app.get("/get", summary="Чтение ключа из Redis Cluster")
async def get_value(
    key: str = Query(..., description="Ключ для чтения")
):
    """
    Считывает значение по ключу из кластера Redis.
    """
    try:
        val = await app.state.redis.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if val is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": val}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
