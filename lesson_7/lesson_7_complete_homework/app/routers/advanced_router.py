# BEGIN YOUR SOLUTION HERE
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Body, Query
from app.schemas import LikeOperation
from app.redis_advanced import (
    update_post_view_atomic,
    bulk_like_operations,
)

router = APIRouter(
    prefix="/advanced",
    tags=["advanced"]
)

@router.post("/view-post-lua/")
async def view_post_lua(post_id: int, user_id: str, request: Request):
    """
    Эндпоинт демонстрирует вызов Lua-скрипта для атомарного обновления просмотра поста.
    """
    # Извлекаем SHA скрипта из app.state
    lua_sha = request.app.state.view_post_lua_sha
    
    # Вызываем функцию, передавая lua_sha
    result = await update_post_view_atomic(
        post_id=post_id,
        user_id=user_id,
        history_limit=10,
        lua_sha=lua_sha
    )
    if result != True:
        raise HTTPException(status_code=400, detail="Lua script execution failed")
    
    return {"detail": f"Post {post_id} viewed by user {user_id} atomically via Lua"}

@router.post("/bulk-likes/", summary="Массовые лайки", response_description="Результаты выполнения пайплайна")
async def do_bulk_likes(
    operations: List[LikeOperation] = Body(
        ...,
        description="Список операций для массовой постановки лайков."
    )
):
    """
    Выполняет массовые операции лайков через Redis-пайплайн.
    
    **Описание**:
    - Получает список операций (каждая представляет данные о посте, пользователе и авторе поста).
    - Для каждого элемента в списке выполняется:
      - `SADD` для добавления лайка в множество `likes:{post_id}`;
      - `ZINCRBY` для увеличения рейтинга автора в `author:rating`.

    **Параметры**:
    - `operations`: список экземпляров `LikeOperation`, содержащих `post_id`, `user_id` и `author_id`.
    """
    ops_data = [op.model_dump() for op in operations]
    results = await bulk_like_operations(ops_data)
    return {"detail": "Bulk likes done", "results": results}
# END