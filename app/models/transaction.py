from sqlmodel import Field, SQLModel
from typing import List, Optional


class Transaction(SQLModel, table=True):
    __tablename__ = "transcaction"
    transaction_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    date: str
    transaction_type: str
    amount: float



