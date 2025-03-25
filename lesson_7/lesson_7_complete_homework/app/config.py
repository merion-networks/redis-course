from pydantic_settings import BaseSettings
from typing import Optional


# Класс для хранения настроек приложения
class Settings(BaseSettings):
    # URL для подключения к базе данных через SQLAlchemy
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Настройки подключения к Redis
    REDIS_HOST: str = "localhost"  # Хост Redis-сервера
    REDIS_PORT: int = 6379  # Порт Redis-сервера
    REDIS_DB: int = 0  # Номер базы Redis
    REDIS_PASSWORD: Optional[str] = None  # Пароль для Redis
    # TTL в секундах
    CACHE_EXPIRE: int = 60

    class Config:
        # Указываем файл .env для загрузки переменных окружения
        env_file = ".env"


# Создаём единственный экземпляр настроек для использования в приложении
settings = Settings()
