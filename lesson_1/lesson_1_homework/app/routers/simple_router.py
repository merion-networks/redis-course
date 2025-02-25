from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from app.database import get_db
from app.models import Item
from app.schemas import Item as ItemSchema, ItemCreate
from app.redis_client import redis_client

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get("/{item_id}", response_model=ItemSchema)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает объект из базы данных по его ID.
    Если объект есть в Redis, возвращает данные из кэша.
    В противном случае извлекает из базы, кэширует и возвращает результат.
    """
    cache_key = f"item:{item_id}"

    # Проверяем, есть ли объект в кэше Redis
    cached_item = await redis_client.get(cache_key)
    if cached_item:
        return json.loads(cached_item)

    # Если объекта нет в кэше, выполняем запрос к базе данных
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Преобразуем объект базы данных в Pydantic-схему
    item_data = ItemSchema.model_validate(item).model_dump()

    # Кэшируем результат в Redis на 60 секунд
    await redis_client.set(cache_key, json.dumps(item_data), ex=60)

    return item_data

# BEGIN YOUR SOLUTION HERE

@router.get("/", response_model=list[ItemSchema])
async def get_all_items(db: AsyncSession = Depends(get_db)):
    """
    Получает все объекты из базы данных.
    Кэширование результата в Redis не требуется.
    """
    result = await db.execute(select(Item))
    items = result.scalars().all()

    return [
        ItemSchema.model_validate(item).model_dump() for item in items
    ]  # Преобразуем в Pydantic-схему


@router.post("/create/", response_model=ItemSchema)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """
    Создание нового предмета.
    Принимает данные из схемы `ItemCreate`, добавляет их в базу данных и возвращает созданный объект.
    """
    new_item = Item(
        name=item.name, description=item.description
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    return new_item


@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: int, item: ItemCreate, db: AsyncSession = Depends(get_db)
):
    """
    Обновляет объект в базе данных и в кэше Redis.
    """

    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item.name
    db_item.description = item.description
    await db.commit()
    await db.refresh(db_item)

    validated_item = ItemSchema.model_validate(db_item).model_dump()

    # Обновляем кэш в Redis
    cache_key = f"item:{item_id}"
    await redis_client.set(cache_key, json.dumps(validated_item), ex=60)

    return validated_item


@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаление объекта из базы данных и кэша Redis.
    """
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(db_item)
    await db.commit()

    # Удаляем объект из кэша
    cache_key = f"item:{item_id}"
    await redis_client.delete(cache_key)

    return {"detail": "Item deleted"}

# END