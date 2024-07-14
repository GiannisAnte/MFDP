from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user import User
from services.user_service import create_user, authenticate, get_user_by_username, get_all_users
from services.balance_servise import get_balance, add_to_balance, deduct_from_balance
from services.task_service import task_history
from services.transaction_service import tr_history
from typing import List

user_route = APIRouter(tags=['User'])

#регистрация
@user_route.post('/signup')
async def signup(username: str, email: str, password: str, session=Depends(get_session)):
    response = create_user(username, email, password, session)
    if response == {'Error: User already exists'}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already exists")
    if response == {"message": "User successfully registered!"}:
        return {"message": "User successfully registered!"}

#авторизация
@user_route.post('/signin')
async def signin(username: str, password: str, session=Depends(get_session)):
    user = get_user_by_username(username, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    response = authenticate(username, password, session)
    if response is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password is incorrect")
    if response is True:
        return {"message": "User signed in successfully"}

#получение списка всех юзеров
@user_route.get('/all_users', response_model=List[User])
async def get_all_users_route(session=Depends(get_session)) -> list:
    return get_all_users(session)

#получение баланса юзера по id
@user_route.get('/balance/{user_id}', response_model=float)
async def get_balance_user(user_id: int, session=Depends(get_session)) -> float:
    balance = get_balance(user_id, session)
    return balance

#пополнение баланса
@user_route.put('/add_coin/{user_id}')
async def add_coin(user_id: int,
                      amount: float,
                      session=Depends(get_session)):
    add_to_balance(user_id, amount, session)
    return {"message": f"Coin added to user (id {user_id})"}

#уменьшение баланса
@user_route.put('/deduct_coin/{user_id}')
async def deduct_coin(user_id: int,
                      amount: float,
                      session=Depends(get_session)):
    deduct_from_balance(user_id, amount, session)
    return {"message": f"Coin deduct from user (id {user_id})"}

#запрос истории транзакций юзера
@user_route.get('/user_transactions/{user_id}')
async def get_transactions(user_id: int, session=Depends(get_session)):
    return tr_history(user_id, session)

#запрос истории задач от юзера
@user_route.get('/user_history/{user_id}')
async def get_history(user_id: int, session=Depends(get_session)):
    return task_history(user_id, session)






