from app.models.user import User
from app.models.admin import Admin


class Auth_Service:
    def __init__(self):
        self.__users = {}

    @staticmethod
    def register(user_id: int, username: str, password: str,
                 email: str, first_name: str, last_name: str) -> str:
        # занесение данных в БД
        ...

    @staticmethod
    def login(username: str, password: str) -> str:
        # Авторизация через проверку логина и пароля в БД
        ...
