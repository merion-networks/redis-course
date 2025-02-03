from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from app.database import get_db
from app.models import Item
from app.schemas import Item as ItemSchema
from app.redis_client import redis_client

router = APIRouter()


@router.get("/{item_id}")
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает объект из базы данных по его ID.
    Если объект есть в Redis, возвращает данные из кэша.
    В противном случае извлекает из базы, кэширует и возвращает результат.
    """
    # Формируем ключ для кэша
    cache_key = f"item:{item_id}"

    # Проверяем, есть ли объект в кэше Redis
    cached_item = await redis_client.get(cache_key)
    if cached_item:
        # Если объект найден в кэше, возвращаем его, предварительно декодировав из JSON
        return json.loads(cached_item)

    # Если объекта нет в кэше, выполняем запрос к базе данных
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    # Если объект не найден, возвращаем ошибку 404
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Преобразуем объект базы данных в Pydantic-схему
    item_data = ItemSchema.model_validate(item).model_dump()

    # Сохраняем результат в Redis с временем жизни 60 секунд
    await redis_client.set(cache_key, json.dumps(item_data), ex=60)

    # Возвращаем данные объекта
    return item_data
