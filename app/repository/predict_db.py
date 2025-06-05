from uuid import UUID
import uuid
from datetime import datetime
# from database.database import get_session
from sqlmodel import Session
from models.prediction import Prediction

def create_predict_event(
    # session: get_session,
    session: Session,
    event_id: str,
    status: str = None,
    model_type: str = None,
    variant: str = None,
    score: float = None,
    result: str = None
) -> Prediction:
    pr = Prediction(
        id=str(uuid.uuid4()),
        fire_event_id=event_id,
        status=status,
        created_at=datetime.utcnow(),
        model_type=model_type,
        variant=variant,
        score=score,
        result=result
    )
    session.add(pr)
    # session.commit()
    # session.refresh(pr)
    return pr