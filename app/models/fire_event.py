from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PGUUID

if TYPE_CHECKING:
    from models.user import User

class FireEvent(SQLModel, table=True):
    __tablename__ = "fire_events"

    id: Optional[UUID] = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),   # нативный UUID
            primary_key=True,
            default=uuid4,          # SQLAlchemy поставит значение по умолчанию
            nullable=False,
        )
    )
    created_by: Optional[UUID] = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id"),
            nullable=True,
        )
    )
    user: Optional['User'] = Relationship(back_populates="fire_events")
    predictions: List["Prediction"] = Relationship(back_populates="fire_event")
    source: str = Field(
        sa_column=Column(
            String(64),
            nullable=False,
        )
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime,
            nullable=False,
        )
    )
    latitude: Optional[float] = Field(
        sa_column=Column(
            Float,
            nullable=True,
        )
    )
    longitude: Optional[float] = Field(
        sa_column=Column(
            Float,
            nullable=True,
        )
    )
    payload: Optional[dict] = Field(
        sa_column=Column(
            JSON,
            nullable=True,
        )
    )
