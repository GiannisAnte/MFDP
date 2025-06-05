from fastapi import APIRouter, Depends
from database.database import get_session
from schemas.Users import Users
from services.user_service import get_all_users, get_username
from typing import List
from core.authenticate import authenticate_cookie
from services.user_service import get_all_his


auth_router = APIRouter(tags=['User'])
get_user_route = APIRouter(tags=['User'])

# @auth_router.get("/auth/{token}")
# async def auth(token: str):
#     """
#     Аутентификация юзера по токену, сервисный эндпоинт, возвращает id юзера
#     """
#     result = await authenticate_cookie(token)
#     return result
@auth_router.get("/auth", summary="Проверка авторизации")
async def auth(user_id: str = Depends(authenticate_cookie)):
    return {"user_id": user_id}

@get_user_route.get('/users', response_model=List[Users], summary="Список всех пользователей")
async def get_all_users_route(
    session = Depends(get_session),
):
    return get_all_users(session)

#запрос имени
@get_user_route.get('/name', summary="Получение имени пользователя")
async def get_name(user_id: str = Depends(authenticate_cookie), session=Depends(get_session)):
    username = get_username(user_id, session)
    return {"username": username}


@get_user_route.get("/history", summary="История действий пользователя")
async def user_history(
    user_id: str = Depends(authenticate_cookie),
    session = Depends(get_session)
) -> list[dict]:
    return get_all_his(session, user_id)

# @get_user_route.get('/history')
# async def get_all_users_his(session=Depends(get_session)):
#     """
#     Получение истории всех предсказаний всех пользователей
#     """
#     return get_all_his(session)