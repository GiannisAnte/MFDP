from services.task_service import task_history, task_predict
from fastapi import APIRouter, HTTPException, status, Depends
from  database.database import get_session
import joblib
from shema.input_data import InputData

ml_route = APIRouter(tags=['ML'])

with open("files_for_ml/diabet_rfc.pkl", 'rb') as file:
    model = joblib.load(file)


#запрос истории задач от юзера
@ml_route.get('/task_history/{user_id}')
async def get_history(user_id: int, session=Depends(get_session)):
    return task_history(user_id, session)

@ml_route.post('/predict')
async def predict(user_id: int, input_data: InputData, session=Depends(get_session)):
    response = task_predict(user_id, input_data, model, session)
    if response == {'Error': 'Model not found'}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Model not found")
    if response:
        return response
    #ПО ЛОГИКЕ Я СЮДА ДОЛЖЕН ПЕРЕДАТЬ RPC_CLIENT (папка rbmq) и каждый раз при вызове этого ендпоинта подцепляется вызов rabbitmq