from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import Column, String, Boolean

if TYPE_CHECKING:
    from models.fire_event import FireEvent

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        sa_column_kwargs={"unique": True}
    )
    username: str = Field(
        sa_column=Column(
            String, 
            unique=True,
            index=True,
            nullable=False
        )
    )
    email: str = Field(
        sa_column=Column(
            String,
            unique=True,
            index=True,
            nullable=False
        )
    )
    hashed_password: str = Field(
        nullable=False)
    is_superuser: bool = Field(
        default=False,
        sa_column=Column(
            Boolean,
            nullable=False
        )
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    fire_events: List['FireEvent'] = Relationship(back_populates="user")
