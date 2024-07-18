from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    email: str
    role: str = Field(default='user')


