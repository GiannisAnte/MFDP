from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    email: str
    balance: float = Field(default=0.0)
    role: str = Field(default='user')

    @property
    def get_user_id(self):
        return self.__id

    @property
    def get_username(self):
        return self.__username

    @property
    def balance(self):
        return self.__balance

    def add_balance(self, amount):
        self.__balance += amount

    def history(self, action):
        self.__activity_history[action] = self.__balance

    @staticmethod
    def __hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def password_verify(self, password: str) -> bool:
        return self.password == self.__hash_password(password)


