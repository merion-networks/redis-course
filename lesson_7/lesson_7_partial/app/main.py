from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.redis_client import redis_client
from app.routers.post_router import router as post_router
from app.routers.auth_router import router as authentifacate_router
from app.routers.author_router import router as author_router
from app.routers.admin_router import router as admin_router
from app.routers.notifications_router import router as notifications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Настройка жизненного цикла приложения:
    - Подключение к базе данных и создание таблиц.
    - Подключение и закрытие Redis.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await redis_client.connect()
    # BEGIN YOUR SOLUTION HERE

    # END
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)


app.include_router(post_router)
app.include_router(authentifacate_router)
app.include_router(author_router)
app.include_router(admin_router)
# BEGIN YOUR SOLUTION HERE
app.include_router(notifications_router)
# END
