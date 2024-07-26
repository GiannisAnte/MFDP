from fastapi import APIRouter, Depends
from database.database import get_session
from shema.Users import Users
from shema.Tasks import Tasks
from models.transaction import Transaction
from models.task import Task
from services.user_service import get_all_users, get_username
from services.balance_servise import get_balance
from services.transaction_service import tr_history, get_all_tr
from services.task_service import get_all_his
from typing import List
from auth.authenticate import authenticate_cookie
from shema.Transactions import Transactions

auth_router = APIRouter(tags=['User'])
get_user_route = APIRouter(tags=['User'])

@auth_router.get("/auth/{token}")
async def auth(token: str):
    """
    Аутентификация юзера по токену, сервисный эндпоинт, response_model=List[User]
    """
    result = await authenticate_cookie(token)
    return result

@get_user_route.get('/users', response_model=Users)
async def get_all_users_route(session=Depends(get_session)) -> list:
    """
    Получение списка всех юзеров
    """
    return get_all_users(session)

@get_user_route.get('/tasks_history', response_model=List[Tasks])
async def get_all_users_his(session=Depends(get_session)) -> list:
    """
    Получение списка всех запросов юзеров
    """
    return get_all_his(session)

@get_user_route.get('/transaction_history', response_model=List[Transactions])
async def get_all_users_tr(session=Depends(get_session)) -> list:
    """
    Получение списка всех транзакций юзеров
    """
    return get_all_tr(session)


@get_user_route.get('/balance/', response_model=float)
async def get_balance_user(token: str, session=Depends(get_session)) -> float:
    """
    Получение баланса юзера
    """
    user_id = int(await authenticate_cookie(token))
    balance = get_balance(user_id, session)
    return balance

@get_user_route.get('/transactions/{token}', response_model=List[Transaction])
async def get_transactions(token: str, session=Depends(get_session)):
    """
    Получение истории транзакций юзера
    """
    user_id = int(await authenticate_cookie(token))
    return tr_history(user_id, session)

#запрос имени
@get_user_route.get('/name/')
async def get_transactions(token: str, session=Depends(get_session)):
    """
    Получение имени юзера, сервисный эндпоинт
    """
    user_id = int(await authenticate_cookie(token))
    return get_username(user_id, session)