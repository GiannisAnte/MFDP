from models.ml_model import Model
from sqlalchemy.orm import Session
from typing import List, Optional


def get_model_by_id(model_id: int, session) -> Optional[Model]:
    """Возврат модели по id"""
    model = session.query(Model).where(Model.id == model_id).first()
    return model
    

def get_model_by_name(model_name: str, session) -> Optional[Model]:
    """Возврат модели по имени"""
    model = session.query(Model).where(Model.name == model_name).first()
    return model

