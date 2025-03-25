from fastapi import FastAPI
import redis.asyncio as aioredis
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = aioredis.Redis(decode_responses=True)
    app.state.redis = redis_client
    
    with open("example.lua", "r") as f:
        lua_script = f.read()
    lua_script_hash = await redis_client.script_load(lua_script)
    app.state.lua_script_hash = lua_script_hash
    yield

    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/pipeline")
async def pipeline_demo(key: str, incr: int, start_value: int):
    redis_client = app.state.redis
    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.set(key, start_value)
        pipe.incrby(key, incr)
        results = await pipe.execute()
    return {"results": results}
    

@app.get("/lua")
async def lua_demo(list_name: str, counter_name: str, increment: int, value: str):
    redis_client = app.state.redis
    lua_script_hash = app.state.lua_script_hash
    result = await redis_client.evalsha(lua_script_hash, 2, counter_name, list_name, increment, value)
    return {"result": result}
