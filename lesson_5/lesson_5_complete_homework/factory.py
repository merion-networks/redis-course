import random
import asyncio
import uuid
import time
from faker import Faker
from app.database import AsyncSessionLocal
from app.models import User, Post
from app.redis_client import redis_client
from app.routers.post_router import read_post, like_post


# Функция для логина пользователя (создаёт сессию в Redis)
async def login_user(user: User):
    token = str(uuid.uuid4())
    session_key = f"session:{token}"
    session_data = {
        "user_id": str(user.id),
        "username": user.username,
        "created_at": str(time.time()),
    }
    await redis_client.redis.hset(session_key, mapping=session_data)
    await redis_client.redis.expire(session_key, 1800)  # TTL 30 минут
    return token, session_data, session_key


# Функция для логаута (удаляет сессию из Redis)
async def logout_user(session_key: str):
    await redis_client.redis.delete(session_key)


# вход, просмотр постов, лайки, выход
async def simulate_user_actions(users: list[User], posts: list[Post]):
    async with AsyncSessionLocal() as session:
        for user in users:
            # Логинимся под пользователем
            token, current_user, session_key = await login_user(user)
            print(f"User {user.username} logged in with token {token}")

            # Случайно выбираем 10 постов для просмотра
            view_posts = random.sample(posts, k=min(3, len(posts)))
            for post in view_posts:
                await read_post(post.id, db=session, current_user=current_user)

            # Случайно выбираем 5 постов (не свои) для лайка
            non_own_posts = [post for post in posts if post.author_id != user.id]
            if non_own_posts:
                like_posts = random.sample(non_own_posts, k=min(5, len(non_own_posts)))
                for post in like_posts:
                    await like_post(post.id, db=session, current_user=current_user)

            # Логаут пользователя
            await logout_user(session_key)
            print(f"User {user.username} logged out.\n")


# Основная функция: создание пользователей, постов и симуляция действий
async def create_data_and_simulate():
    fake = Faker()
    await redis_client.connect()

    users = []
    posts = []

    # Создаем пользователей и посты через SQLAlchemy
    async with AsyncSessionLocal() as session:
        # Создаем 100 пользователей с уникальными именами и username
        for _ in range(100):
            user = User(
                name=fake.name(),
                username=fake.unique.user_name(),
                hashed_password="password",  # Для теста используем статичный пароль
            )
            session.add(user)
            users.append(user)
        await session.commit()
        for user in users:
            await session.refresh(user)

        # Для каждого пользователя создаем 2-6 поста с рандомными заголовками и описаниями
        for user in users:
            num_posts = random.randint(2, 6)
            for _ in range(num_posts):
                post = Post(
                    name=fake.sentence(nb_words=6),
                    description=fake.paragraph(nb_sentences=3),
                    author_id=user.id,
                )
                session.add(post)
                posts.append(post)
        await session.commit()
        for post in posts:
            await session.refresh(post)

    print(f"Created {len(users)} users and {len(posts)} posts.\n")

    # Симулируем действия каждого пользователя (вход, просмотры, лайки, выход)
    await simulate_user_actions(users, posts)
    await redis_client.close()


if __name__ == "__main__":
    asyncio.run(create_data_and_simulate())
