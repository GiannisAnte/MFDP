from typing import List, Dict, Any
from services.task_service import task_history, task_predict
from fastapi import APIRouter, Depends
from  database.database import get_session
from models.task import Task
import joblib
from shema.input_data import InputData


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

@ml_route.post('/predict', response_model=Dict[str, str])
async def predict(user_id: int, input_data: InputData, session=Depends(get_session)):
    return task_predict(user_id, input_data, session)
