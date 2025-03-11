from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.redis_client import redis_client

router = APIRouter(
    prefix="/authors",
    tags=["authors"],
)


@router.get("/top", response_model=List[UserOut])
async def get_top_authors(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Возвращает топ-авторов по рейтингу, хранящемуся в Redis Sorted Set "author:rating".
    """
    top_author_ids = await redis_client.redis.zrevrange("author:rating", 0, limit - 1)
    authors = []
    for author_id in top_author_ids:
        result = await db.execute(select(User).where(User.id == int(author_id)))
        user = result.scalar_one_or_none()
        if user:
            authors.append(user)
    return authors
