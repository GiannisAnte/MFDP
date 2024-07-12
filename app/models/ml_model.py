from sqlmodel import SQLModel, Field
from typing import Optional

class Model(SQLModel, table=True):
    __tablename__ = "mlmodel"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    path: str
    cost: float

