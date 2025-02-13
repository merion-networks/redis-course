import redis.asyncio as aioredis
from fastapi import FastAPI, Body
from contextlib import asynccontextmanager
from faker import Faker


# Подключаемся к Redis (асинхронный клиент)
redis_client = aioredis.Redis(host="localhost", port=6379, decode_responses=True)


# Создаём фейковые профили пользователей
# (В домашнем задании вам необходимо хранить их в БД)
def make_profiles():
    fake = Faker("ru_Ru")
    batch_profiles = {}
    for i in range(1, 11):
        batch_profiles[i] = {
            "name": fake.name(),
            "email": fake.email(),
            "age": str(fake.random_int(18, 55)),  # Сохраняем возраст строкой для Redis
        }
    return batch_profiles


db = make_profiles()


async def startup_event():
    """
    При старте приложения можем автоматически загрузить
    сгенерированные профили в Redis (по желанию).
    """
    for user_id, profile in db.items():
        key = f"user:{user_id}:profile"
        # Сохраняем каждое поле фейкового профиля в хэше
        await redis_client.hset(key, mapping=profile)


# Управление жизненным циклом приложения через lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield


app = FastAPI(lifespan=lifespan)

# СЧЁТЧИК


@app.post("/increment")
async def increment_counter():
    """
    Инкрементируем глобальный счётчик my_counter в Redis.
    При первом вызове ключ создаётся с начальным значением 1.
    """
    new_value = await redis_client.incr("my_counter")
    return {"my_counter": new_value}


@app.get("/value")
async def get_value():
    """
    Получаем текущее значение счётчика my_counter.
    Если ключ отсутствует в Redis, вернётся None.
    """
    val = await redis_client.get("my_counter")
    return {"my_counter": val}


# ПРОФИЛИ


@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: int):
    """
    Извлекает полный профиль пользователя в виде хэша из Redis.
    """
    key = f"user:{user_id}:profile"
    user_profile = await redis_client.hgetall(key)
    if not user_profile:
        return {"error": "User not found or profile is empty"}
    return {"profile": user_profile}


@app.put("/user/{user_id}/profile")
async def update_user_profile(user_id: int, profile: dict = Body(...)):
    """
    Обновляет поля хэша (профиля пользователя) в Redis.
    Пример тела запроса:
    {
      "name": "Иван Иванов",
      "email": "ivan@example.com",
      "age": "30"
    }
    """
    key = f"user:{user_id}:profile"
    # Обновляем поля хэша. mapping позволяет задать сразу несколько полей
    await redis_client.hset(key, mapping=profile)
    return {"status": "updated"}


@app.delete("/user/{user_id}/profile")
async def delete_user_profile(user_id: int):
    """
    Полностью удаляет профиль пользователя (ключ в Redis).
    """
    key = f"user:{user_id}:profile"
    deleted_count = await redis_client.delete(key)
    if deleted_count == 0:
        return {"status": "no key found"}
    return {"status": "deleted"}


@app.delete("/user/{user_id}/profile/{field}")
async def delete_user_profile_field(user_id: int, field: str):
    """
    Удаляет конкретное поле в хэше профиля.
    Пример: DELETE /user/1/profile/age — удалит поле "age".
    """
    key = f"user:{user_id}:profile"
    removed_fields = await redis_client.hdel(key, field)
    if removed_fields == 0:
        return {"status": f"field '{field}' not found or no user"}
    return {"status": f"field '{field}' deleted"}
