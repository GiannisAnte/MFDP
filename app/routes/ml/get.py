from typing import List, Dict, Any
from services.task_service import task_history
from fastapi import APIRouter, Depends
from  database.database import get_session
from models.task import Task
from auth.authenticate import authenticate_cookie

get_ml_route = APIRouter(tags=['ML'])


@get_ml_route.get('/task_history/{token}', response_model=List[Task])
async def get_history(token: str, session=Depends(get_session)) -> List[Dict[str, Any]]:
    """
    Возврат истории запросов юзера
    """
    user_id = int(await authenticate_cookie(token))
    return task_history(user_id, session)