from typing import List, Dict
from services.task_service import task_predict
from fastapi import APIRouter, Depends
from  database.database import get_session
from shemas.input_data import InputData
from auth.authenticate import authenticate_cookie

post_ml_route = APIRouter(tags=['ML'])


@post_ml_route.post('/predict/{token}', response_model=Dict[str, str])
async def predict(token: str, input_data: InputData, session=Depends(get_session)):
    """
    Возврат ответа модели на запрос юзера
    """
    user_id = int(await authenticate_cookie(token))
    return task_predict(user_id, input_data, session)