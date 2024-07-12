from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime


class Task(SQLModel, table=True):
    action_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    amount: float
    response: str
    

