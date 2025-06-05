import os
from typing import Generator, Optional

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

from database.config import get_settings
from models.fire_event import FireEvent   #Обязательно импортировать, чтобы таблица зарегалась
from models.prediction import Prediction   #То же самое
from models.user import User              
from core.hash_password import HashPassword#create_hash

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

settings = get_settings()
raw_url = settings.DATABASE_URL_psycopg2

if not raw_url or str(raw_url).lower() == "none":
    db_url = "sqlite:///:memory:"
    connect_args = {"check_same_thread": False}
    echo = False
else:
    db_url = raw_url
    connect_args = {}
    echo = False

engine: Engine = create_engine(
    url=db_url,
    echo=echo,
    pool_size=getattr(settings, "POOL_SIZE", 5),
    max_overflow=getattr(settings, "MAX_OVERFLOW", 10),
    pool_pre_ping=True,
    pool_recycle=getattr(settings, "POOL_RECYCLE", 3600),
    connect_args=connect_args
)

hash_password = HashPassword()

def get_session() -> Generator[Session, None, None]:
    """
    Зависимость для FastAPI: при каждом запросе создаётся и возвращается новая сессия.
    """
    with Session(engine) as session:
        yield session


def create_session() -> Session:
    """
    Функция для ручного получения Session (вне FastAPI-Depends).
    """
    return Session(engine)


def create_superuser() -> None:
    """
    Создаёт суперпользователя (admin), если его ещё нет.
    Пароль берётся из переменной окружения ADMIN_PASSWORD.
    """
    with Session(engine) as session:
        existing_admin = session.query(User).filter_by(is_superuser=True).first()
        if not existing_admin:
            password = os.getenv("ADMIN_PASSWORD", "")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password.create_hash(password),
                is_superuser=True
            )
            session.add(admin_user)
            session.commit()
            print("Суперпользователь создан")


def create_user() -> None:
    """
    Создаёт демо-пользователя (username="a", password="a").
    """
    with Session(engine) as session:
        user = User(
            username="a",
            email="a@example.com",
            hashed_password=hash_password.create_hash("a"),
            is_superuser=False
        )
        session.add(user)
        session.commit()


def init_db() -> None:
    """
    Полная инициализация БД:
    1) Сброс всех таблиц (drop_all)
    2) Создание всех таблиц (create_all)
    3) Создание суперпользователя и демо-пользователя
    """
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    create_superuser()
    create_user()


# from sqlmodel import SQLModel, Session, create_engine
# from sqlalchemy.orm import sessionmaker
# from database.config import get_settings
# from models.fire_event import FireEvent
# from models.prediction import Prediction #обе необходимы тут для создания таблиц, без не сработает
# from models.user import User
# from core.hash_password import create_hash
# import os
# from dotenv import load_dotenv

# env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))
# load_dotenv(env_path)

# engine = create_engine(url=get_settings().DATABASE_URL_psycopg2,
#                        echo=False, pool_size=5, max_overflow=10)

# # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_session():
#     with Session(engine) as session:
#         yield session

# def create_session() -> Session:
#     return Session(engine)


# def create_superuser():
#     with Session(engine) as session:
#         # Проверка: есть ли уже админ
#         existing_admin = session.query(User).filter_by(is_superuser=True).first()
#         if not existing_admin:
#             admin_user = User(
#                 username="admin",
#                 email="admin@example.com",
#                 hashed_password=create_hash(os.getenv("ADMIN_PASSWORD")),
#                 is_superuser=True
#             )
#             session.add(admin_user)
#             session.commit()
#             print("Администратор создан")

# def create_user():
#     with Session(engine) as session:
#         user = User(
#                 username="a",
#                 email="a@example.com",
#                 hashed_password=create_hash('a'),
#                 is_superuser=False
#             )
#         session.add(user)
#         session.commit()

# def init_db():
#     """Инициализация базы данных"""
#     SQLModel.metadata.drop_all(engine)
#     SQLModel.metadata.create_all(engine)
#     create_superuser()
#     create_user()
