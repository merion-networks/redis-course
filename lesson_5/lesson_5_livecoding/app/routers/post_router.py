from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from app.database import get_db
from app.models import Post
from app.schemas import Post as PostSchema, PostCreate
from app.redis_client import redis_client

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


# Зависимость для получения сессионных данных
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token = auth_header.split(" ")[1]
    session_key = f"session:{token}"
    session_data = await redis_client.redis.hgetall(session_key)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return session_data


# Зависимость для получения сессионных данных, либо None (когда аутентификация неважна)
async def get_current_user_optional(request: Request) -> Optional[dict]:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        session_key = f"session:{token}"
        session_data = await redis_client.redis.hgetall(session_key)
        if session_data:
            return session_data
    return None


@router.get("/me", response_model=List[PostSchema])
async def get_my_posts(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Возвращает посты, созданные текущим аутентифицированным пользователем.
    """
    user_id = int(current_user["user_id"])
    result = await db.execute(select(Post).where(Post.author_id == user_id))
    posts = result.scalars().all()
    return [PostSchema.model_validate(post).model_dump() for post in posts]


# -- Реализация топ 10 постов --


@router.get("/top", response_model=List[PostSchema])
async def get_top_posts(db: AsyncSession = Depends(get_db), limit: int = 10):
    """
    Возвращает топ-постов по количеству просмотров, используя отсортированное множество.
    Из множества с ключом 'post:views:ranking' извлекаются ID постов с наибольшим счётом.
    """
    # Получаем рейтинг постов по просмотрам
    top_ids = await redis_client.redis.zrevrange("post:views:ranking", 0, limit - 1)
    posts = []
    for pid in top_ids:
        result = await db.execute(select(Post).where(Post.id == int(pid)))
        post = result.scalar_one_or_none()
        if post:
            posts.append(PostSchema.model_validate(post).model_dump())
    return posts


@router.get("/{post_id}", response_model=PostSchema)
async def read_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Получает пост по ID.
    Если пост найден в кэше Redis, возвращает его, иначе – извлекает из базы, кэширует и возвращает.
    Если пользователь аутентифицирован, записывает просмотр в историю.
    Обновляет рейтинг просмотров.
    """
    cache_key = f"post:{post_id}"
    cached_post = await redis_client.get(cache_key)
    if cached_post:
        post_data = json.loads(cached_post)
    else:
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        post_data = PostSchema.model_validate(post).model_dump()
        await redis_client.set(cache_key, json.dumps(post_data), ex=60)

    # Увеличиваем счётчик просмотров для данного поста в рейтинге постов
    await redis_client.redis.zincrby("post:views:ranking", 1, post_id)

    # Если пользовватель аутентифицирован сохраняем id поста в его истории просмотров
    if current_user:
        views_key = f"views:{current_user['user_id']}"
        await redis_client.redis.lpush(views_key, post_id)
        # Ограничиваем историю 10 последними просмотрами
        await redis_client.redis.ltrim(views_key, 0, 9)

    return post_data


@router.get("/", response_model=List[PostSchema])
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    """
    Возвращает все посты.
    """
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return [PostSchema.model_validate(post).model_dump() for post in posts]


@router.post("/create/", response_model=PostSchema)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Создаёт новый пост.
    Автором становится текущий аутентифицированный пользователь.
    """
    user_id = int(current_user["user_id"])
    new_post = Post(name=post.name, description=post.description, author_id=user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.put("/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: int,
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Обновляет пост.
    Доступно только для автора поста.
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if int(current_user["user_id"]) != db_post.author_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )

    db_post.name = post.name
    db_post.description = post.description
    await db.commit()
    await db.refresh(db_post)

    validated_post = PostSchema.model_validate(db_post).model_dump()
    cache_key = f"post:{post_id}"
    await redis_client.set(cache_key, json.dumps(validated_post), ex=60)
    return validated_post


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Удаляет пост.
    Доступно только для автора поста.
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if int(current_user["user_id"]) != db_post.author_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )

    await db.delete(db_post)
    await db.commit()
    cache_key = f"post:{post_id}"
    await redis_client.delete(cache_key)
    return {"detail": "Post deleted"}


@router.post("/{post_id}/like/")
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Позволяет аутентифицированному пользователю поставить лайк посту.
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    key = f"likes:{post_id}"
    added = await redis_client.redis.sadd(key, current_user["user_id"])
    if added:
        # Если лайк поставлен впервые, увеличиваем рейтинг автора
        author_rating_key = "author:rating"
        await redis_client.redis.zincrby(author_rating_key, 1, db_post.author_id)
    return {"detail": f"Post {post_id} liked by user {current_user['user_id']}"}


@router.post("/{post_id}/unlike/")
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Позволяет аутентифицированному пользователю убрать лайк с поста.
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    key = f"likes:{post_id}"
    removed = await redis_client.redis.srem(key, current_user["user_id"])
    if removed:
        # Если лайк успешно убран, уменьшаем рейтинг автора
        author_rating_key = "author:rating"
        await redis_client.redis.zincrby(author_rating_key, -1, db_post.author_id)
        return {"detail": f"User {current_user['user_id']} unliked post {post_id}"}
    else:
        return {
            "detail": f"User {current_user['user_id']} had not liked post {post_id}"
        }


@router.get("/{post_id}/likes/")
async def get_likes_count(post_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает количество лайков для поста.
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    key = f"likes:{post_id}"
    likes_count = await redis_client.redis.scard(key)
    return {"post_id": post_id, "likes_count": likes_count}


@router.get("/{post_id}/likes/check/")
async def check_if_liked(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Проверяет, поставил ли текущий пользователь лайк посту.
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    key = f"likes:{post_id}"
    liked = await redis_client.redis.sismember(key, current_user["user_id"])
    return {"post_id": post_id, "liked": liked}


@router.get("/views/history", response_model=List[PostSchema])
async def get_view_history(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Возвращает список постов из истории просмотров текущего пользователя.
    """
    views_key = f"views:{current_user['user_id']}"
    # Получаем список идентификаторов постов (строковые значения)
    post_ids = await redis_client.redis.lrange(views_key, 0, -1)
    posts = []
    for pid in post_ids:
        result = await db.execute(select(Post).where(Post.id == int(pid)))
        post = result.scalar_one_or_none()
        if post:
            posts.append(PostSchema.model_validate(post).model_dump())
    return posts
