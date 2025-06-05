from models.user import User
from typing import List, Optional
from pydantic import ValidationError
from datetime import datetime
from sqlmodel import Session, select
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from core.hash_password import HashPassword#create_hash
from uuid import UUID
from models.fire_event import FireEvent
from models.prediction import Prediction

hash_password = HashPassword()

def create_user(username: str, email: str, password: str, session) -> dict:
    """Создание пользователя"""
    if session.query(User).filter(User.username == username).first():
        return {"error": "Username already exists"}
    if session.query(User).filter(User.email == email).first():
        return {"error": "Email already exists"}
    
    hashed_pw = hash_password.create_hash(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_pw,
        is_superuser=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User successfully registered!"}


def get_all_users(session) -> List[User]:
    """Возврат списка всех пользователей"""
    return session.query(User).all()

def get_user(user_id: UUID, session: Session) -> Optional[User]:
    """
    Возвращает User по его UUID, либо None, если не найден.
    """
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement).first()
    return result

def get_user_by_username(username: str, session: Session) -> Optional[User]:
    return session.query(User).filter(User.username == username).first()


def get_username(user_id: UUID, session: Session) -> Optional[str]:
    user = session.query(User).filter(User.id == user_id).first()
    return user.username if user else None



def get_all_his(session: Session, user_id: UUID) -> List[dict]:
    records = (
        session.query(Prediction, FireEvent)
        .join(FireEvent, FireEvent.id == Prediction.fire_event_id)
        .filter(FireEvent.created_by == user_id)
        .all()
    )

    return [
        {
            "fire_event_id": pred.fire_event_id,
            "source": fire.source,
            "latitude": fire.latitude,
            "longitude": fire.longitude,
            "payload": fire.payload,
            "variant": pred.variant,
            "result": pred.result,
            "score": pred.score,
        }
        for pred, fire in records
    ]


# def get_all_his(session):
#     tasks = (
#     session.query(Prediction, FireEvent)
#     .join(FireEvent, FireEvent.id == Prediction.fire_event_id)
#     .all()
#     )

#     data = []
#     for prediction, fire_event in tasks:
#         data.append({
#             "fire_event_id": prediction.fire_event_id,
#             "source": fire_event.source,
#             "latitude": fire_event.latitude,
#             "longitude": fire_event.longitude,
#             "payload": fire_event.payload,
#             "variant": prediction.variant,
#             "result": prediction.result,
#             "score": prediction.score,
#         })

#     return JSONResponse(content=jsonable_encoder(data))