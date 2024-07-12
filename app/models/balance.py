from sqlmodel import Field, SQLModel
from typing import List, Optional


class Balance(SQLModel, table=True):
    __tablename__ = "balance"
    balance_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    user_balance: float
