from fastapi import FastAPI
from app.routers.simple_router import router
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.redis_client import redis_client


# Управление жизненным циклом приложения через lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Настройка жизненного цикла приложения:
    - Подключение к базе данных и создание таблиц.
    - Подключение и закрытие Redis.
    """
    # Подключение к базе данных и создание таблиц, если их ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Подключение к Redis
    await redis_client.connect()

    # Передача управления приложению
    yield

    # Закрытие подключения к Redis
    await redis_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
