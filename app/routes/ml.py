from typing import List, Dict, Any
from services.task_service import task_history, task_log
from services.user_service import get_user
from services.balance_servise import deduct_from_balance, get_balance
from fastapi import APIRouter, HTTPException, status, Depends
from utils.validation import validate_data
from  database.database import get_session
from models.task import Task
import joblib
from shema.input_data import InputData
import rpc_client
import json

ml_route = APIRouter(tags=['ML'])


global model
try:
    with open("files_for_ml/diabet_rfc.pkl", 'rb') as file:
        model = joblib.load(file)
except:
    model = None


#запрос истории задач от юзера
@ml_route.get('/task_history/{user_id}', response_model=List[Task])
async def get_history(user_id: int, session=Depends(get_session)) -> List[Dict[str, Any]]:
    return task_history(user_id, session)

@ml_route.post('/predict')
async def predict(user_id: int, input_data: InputData, session=Depends(get_session)):
    cost = 10.0
    #валидация
    if validate_data(input_data):
        message = validate_data(input_data)
        return {'Error, not valid data' : message}
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

    
