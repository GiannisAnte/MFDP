from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Float, Any, JSON

class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    fire_event_id: UUID = Field(
        foreign_key="fire_events.id",
        nullable=False
    )
    fire_event: Optional["FireEvent"] = Relationship(back_populates="predictions")
    status: str = Field(
        default="pending",
        sa_column=Column(String(20), nullable=False)
    )  #Column(String(20), default="pending") pending/processing/completed/failed
    model_type: str = Field(
        sa_column=Column(String(32), nullable=True) #xgboost или cnn
    )
    variant: Optional[str] = Field(
        sa_column=Column(String(32), nullable=True) # high_recall, high_precision,balanced,cnn,ensemble_vote
 
    )
    result: Optional[str] = Field(
        sa_column=Column(String(32), nullable=True) # no fire / fire
 
    )
    score: float = Field(
        sa_column=Column(Float, nullable=True) #предикт от 0 до 1
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    payload: Optional[dict] = Field(
        sa_column=Column(
            JSON,
            nullable=True,
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "fire_event_id": str(self.fire_event_id),
            "status": self.status,
            "model_type": self.model_type,
            "variant": self.variant,
            "result": self.result,
            "score": self.score,
            "created_at": self.created_at.isoformat()
        }