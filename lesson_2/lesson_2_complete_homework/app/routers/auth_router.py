# BEGIN YOUR SOLUTION HERE
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import time

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, LoginRequest, LoginResponse
from app.redis_client import redis_client
from passlib.context import CryptContext

# Настраиваем логгер
logger = logging.getLogger("auth")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Создаем контекст для хэширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint для регистрации пользователя.
    Проверяет уникальность username, хэширует пароль и сохраняет данные в базе.
    """
    logger.debug(f"[REGISTER] Получены данные для регистрации: {user}")
    # Проверяем, не зарегистрирован ли уже пользователь с таким username
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        logger.debug(
            f"[REGISTER] Пользователь с логином {user.username} уже существует"
        )
        raise HTTPException(
            status_code=400, detail="Пользователь с таким логином уже зарегистрирован"
        )

    # Хэшируем пароль
    hashed_password = pwd_context.hash(user.password)
    logger.debug(f"[REGISTER] Хэш для пароля '{user.password}': {hashed_password}")
    new_user = User(
        name=user.name, username=user.username, hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.debug(f"[REGISTER] Пользователь успешно зарегистрирован: {new_user}")
    return new_user


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint для логина.
    Если количество неудачных попыток превышает порог, блокирует логин на 5 минут.
    При успешной аутентификации сбрасывает счётчик неудачных попыток.
    """
    logger.debug(f"[LOGIN] Попытка входа для пользователя: {login_data.username}")
    failed_key = f"failed:{login_data.username}"
    # Сначала проверяем, превышен ли порог неудачных попыток
    attempts = await redis_client.redis.get(failed_key)
    logger.debug(f"[LOGIN] Текущее количество неудачных попыток: {attempts}")
    if attempts and int(attempts) >= 3:
        logger.debug(f"[LOGIN] Блокировка входа для пользователя {login_data.username}")
        raise HTTPException(
            status_code=403, detail="Слишком много неудачных попыток. Попробуйте позже."
        )

    # Поиск пользователя в базе
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    if not user:
        logger.debug(f"[LOGIN] Пользователь {login_data.username} не найден в базе")
    else:
        logger.debug(
            f"[LOGIN] Найден пользователь: {user.username}, хэш пароля: {user.hashed_password}"
        )

    # Если пользователя не найден или неверный пароль, увеличиваем счётчик
    if not user or not pwd_context.verify(login_data.password, user.hashed_password):
        logger.debug(f"[LOGIN] Неверный пароль для пользователя {login_data.username}")
        # Увеличиваем счётчик неудачных попыток
        attempts = await redis_client.redis.incr(failed_key)
        logger.debug(f"[LOGIN] Обновлённое количество неудачных попыток: {attempts}")
        if attempts == 1:
            # Устанавливаем TTL на 5 минут
            await redis_client.redis.expire(failed_key, 300)
            logger.debug(f"[LOGIN] Установлен TTL 5 минут для ключа {failed_key}")
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

    # При успешной аутентификации сбрасываем счётчик неудачных попыток
    await redis_client.redis.delete(failed_key)
    logger.debug(f"[LOGIN] Сброшены неудачные попытки для {login_data.username}")

    # Генерируем уникальный токен сессии
    token = str(uuid.uuid4())
    session_key = f"session:{token}"
    session_data = {
        "user_id": user.id,
        "username": user.username,
        "created_at": str(time.time()),
    }
    # Сохраняем данные сессии в Redis с TTL 30 минут
    await redis_client.redis.hset(session_key, mapping=session_data)
    await redis_client.redis.expire(session_key, 1800)
    logger.debug(f"[LOGIN] Сессия создана: {session_key} с данными {session_data}")
    return {"token": token}


@router.post("/logout")
async def logout(request: Request):
    """
    Endpoint для выхода из системы.
    Ожидается, что сессионный токен передается в заголовке Authorization в формате 'Bearer <token>'.
    Удаляет сессионный токен из Redis.
    """
    auth_header = request.headers.get("Authorization")
    logger.debug(f"[LOGOUT] Заголовок авторизации: {auth_header}")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.debug("[LOGOUT] Отсутствует или неверный заголовок авторизации")
        raise HTTPException(
            status_code=401, detail="Отсутствует или неверный заголовок авторизации"
        )
    token = auth_header.split(" ")[1]
    session_key = f"session:{token}"
    await redis_client.redis.delete(session_key)
    logger.debug(f"[LOGOUT] Сессия {session_key} удалена")
    return {"detail": "Вы успешно вышли из системы"}
# END
