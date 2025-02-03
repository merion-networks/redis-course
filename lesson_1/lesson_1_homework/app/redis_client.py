import redis.asyncio as redis
from app.config import settings


# Класс для управления подключением к Redis
class RedisClient:
    def __init__(self):
        self.redis = None  # Поле для хранения экземпляра клиента Redis

    async def connect(self):
        """
        Устанавливает подключение к Redis с параметрами из настроек.
        """
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,  # Хост Redis-сервера
            port=settings.REDIS_PORT,  # Порт Redis-сервера
            db=settings.REDIS_DB,  # Номер базы в Redis
            password=settings.REDIS_PASSWORD,  # Пароль для подключения (если требуется)
            decode_responses=True,  # Автоматическое декодирование ответов
        )

    async def close(self):
        """
        Закрывает соединение с Redis, если оно существует.
        """
        if self.redis:
            self.redis.close()  # Закрытие соединения

    async def get(self, key):
        """
        Получает значение из Redis по ключу.
        :param key: Ключ, по которому нужно получить данные.
        :return: Значение, связанное с ключом, или None.
        """
        return await self.redis.get(key)

    async def set(self, key, value, ex=None):
        """
        Устанавливает значение в Redis по ключу.
        :param key: Ключ.
        :param value: Значение, которое нужно сохранить.
        :param ex: Время жизни ключа в секундах (TTL).
        :return: True, если операция успешна.
        """
        return await self.redis.set(key, value, ex=ex)

    async def delete(self, key):
        """
        Удаляет ключ из Redis.
        :param key: Ключ, который нужно удалить.
        :return: Количество удалённых ключей (0 или 1).
        """
        return await self.redis.delete(key)


# Создаём экземпляр клиента Redis для использования в приложении
redis_client = RedisClient()
