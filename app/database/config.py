from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# путь к .env файлу
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))

load_dotenv(env_path)


class Settings(BaseSettings):
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    COOKIE_NAME: Optional[str] = None


    # @property
    # def DATABASE_URL_asyncpg(self):
    #     self._check_all_vars()
    #     return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @property
    def DATABASE_URL_psycopg2(self):
        return f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"
        extra = "ignore"  # Игнорировать дополнительные переменные окружения


@lru_cache()
def get_settings() -> Settings:
    return Settings()

