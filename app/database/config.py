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

    @property
    def DATABASE_URL_asyncpg(self):
        self._check_all_vars()
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @property
    def DATABASE_URL_psycopg2(self):
        # self._check_all_vars()
        return f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    # def _check_all_vars(self):
    #     print(f"POSTGRES_HOST: {self.POSTGRES_HOST}")
    #     print(f"POSTGRES_PORT: {self.POSTGRES_PORT}")
    #     print(f"POSTGRES_USER: {self.POSTGRES_USER}")
    #     print(f"POSTGRES_PASSWORD: {self.POSTGRES_PASSWORD}")
    #     print(f"POSTGRES_DB: {self.POSTGRES_DB}")
    #
    #     if None in {self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_USER, self.POSTGRES_PASSWORD,
    #                 self.POSTGRES_DB}:
    #         raise ValueError("One or more POSTGRES environment variables are not set.")

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"
        extra = "ignore"  # Игнорировать дополнительные переменные окружения


@lru_cache()
def get_settings() -> Settings:
    return Settings()

