from services.task_service import task_history, task_predict
from fastapi import APIRouter, HTTPException, status, Depends
from  database.database import get_session

ml_route = APIRouter(tags=['ML'])


#запрос истории задач от юзера
@ml_route.get('/get_history/{user_id}')
async def get_history(user_id: int, session=Depends(get_session)):
    return task_history(user_id, session)


@ml_route.post('/predict')
async def predict(user_id: int, model_id: int, session=Depends(get_session)):
    response = task_predict(user_id, model_id, session)
    if response == {'Error': 'Model not found'}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Model not found")
    if response == {'message': 'Task created'}:
        return {"Task created"}