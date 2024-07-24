from typing import List, Dict, Any
from services.task_service import task_history, task_predict
from fastapi import APIRouter, Depends
from  database.database import get_session
from models.task import Task
import joblib
from shema.input_data import InputData
from auth.authenticate import authenticate_cookie


ml_route = APIRouter(tags=['ML'])


global model
try:
    with open("files_for_ml/diabet_rfc.pkl", 'rb') as file:
        model = joblib.load(file)
except:
    model = None

@ml_route.get('/task_history/{token}', response_model=List[Task])
async def get_history(token: str, session=Depends(get_session)) -> List[Dict[str, Any]]:
    user_id = int(await authenticate_cookie(token))
    return task_history(user_id, session)

@ml_route.post('/predict/{token}', response_model=Dict[str, str])
async def predict(token: str, input_data: InputData, session=Depends(get_session)):
    user_id = int(await authenticate_cookie(token))
    return task_predict(user_id, input_data, session)

