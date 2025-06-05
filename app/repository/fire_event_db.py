from uuid import UUID
from datetime import datetime
# from database.database import get_session
from sqlmodel import Session
from typing import Optional
from models.fire_event import FireEvent

def create_fire_event(
    session: Session,
    created_by: Optional[UUID],
    source: str,
    event_id: UUID,
    payload: dict= None,
    latitude: float = None,
    longitude: float = None,
) -> FireEvent:
    fe = FireEvent(
        id=event_id,
        created_by=created_by,
        source=source,
        timestamp=datetime.utcnow(),
        latitude=latitude,
        longitude=longitude,
        payload=payload,
    )
    session.add(fe)
    # session.commit()
    # session.refresh(fe) делаем общий коммит в роуте
    return fe
