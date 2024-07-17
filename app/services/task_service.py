from models.task import Task
from models.ml_model import Model
from services.ml_service import get_model_by_id
from shema.input_data import InputData
import pandas as pd
from typing import List, Optional


def task_log(request: Task, session) -> None:
    """Запись действия в БД"""
    session.add(request)
    session.commit()
    session.refresh(request)


def task_history(user_id: int, session) -> List[Task]:
    """История действий"""
    req_history = (session.query(Task)
                   .where(Task.user_id == user_id)
                   .all())
    return req_history

# def task_predict(user_id: int, input_data: InputData, model, session) -> str:
#     # model = get_model_by_id(model_id, session)
#     data = pd.DataFrame([input_data.dict()])
#     predict = model.predict(data)[0]

#     # Логирование предсказания
#     new_task = Task(user_id=user_id, amount=10, response=str(predict))
#     task_log(new_task, session)
#     # session.add(model)
#     session.add(new_task)
#     session.commit()
#     # session.refresh(model)
#     session.refresh(new_task)
#     return {"predicted_status": float(predict)}