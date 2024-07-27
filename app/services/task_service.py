from models.task import Task
from models.user import User
from shemas.input_data import InputData
from shemas.Tasks import Tasks
from typing import List
import rpc_client
from fastapi import APIRouter, HTTPException, status, Depends
from services.user_service import get_user
from services.balance_servise import deduct_from_balance, get_balance
import joblib
from sqlalchemy import join
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

global model
try:
    with open("files_for_ml/diabet_rfc.pkl", 'rb') as file:
        model = joblib.load(file)
except:
    model = None

def get_all_his(session) -> List[Tasks]:
    """Возврат запросов всех пользователей"""
    # return session.query(Task).all()
    tasks = (
    session.query(User, Task)
    .join(Task, User.id == Task.user_id)
    .all()
    )

    tasks_data = []
    for user, task in tasks:
        tasks_data.append({
        'id запроса': task.action_id,
        'id юзера': task.user_id,
        'имя юзера': user.username,
        'стоимость запроса': task.amount,
        'исходные данные пользователя': task.input_data,
        'ответ модели': task.response,
    })

    return JSONResponse(content=jsonable_encoder(tasks_data))


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

def task_predict(user_id: int, input_data: InputData, session):
    cost = 10.0
    request_json = input_data.model_dump_json()
    rpc_cl = rpc_client.RpcClient()
    response = rpc_cl.call(request_json)
    user = get_user(user_id, session)
    #не найден юзер
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User not found")
    #проверка баланса на списание цены предикта
    if get_balance(user.id, session) < cost:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Not enougn coins") 
    #не найден модель  
    if model is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Model not found")
    if response:
        new_task = Task(user_id=user_id, amount=10, input_data=request_json , response=str(response['predicted_status']))
        deduct_from_balance(user.id, cost, session)
        task_log(new_task, session)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return response
