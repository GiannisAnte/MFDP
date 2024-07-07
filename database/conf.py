from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))
load_dotenv(env_path)

# Сформировать SQLALCHEMY_DATABASE_URL
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}?client_encoding=utf8"
)

# Создать engine для соединения с PostgreSQL
engine = create_engine(DATABASE_URL, connect_args={"options": "client_encoding=utf8"})


# Создать класс SessionLocal для создания сессий SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создать базовый класс для всех ORM-моделей
Base = declarative_base()

# Определение модели User
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    age = Column(Integer)
    sex = Column(Boolean)

# Создать таблицу в базе данных
Base.metadata.create_all(engine)
