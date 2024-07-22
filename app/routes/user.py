from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user import User
from models.transaction import Transaction
from models.task import Task
from services.user_service import create_user, get_user_by_username, get_all_users, get_username
from services.balance_servise import get_balance, add_to_balance, deduct_from_balance
from services.transaction_service import tr_history, get_all_tr
from services.task_service import get_all_his
from auth.hash_password import verify_hash
from auth.jwt_handler import create_access_token
from typing import List
from auth.authenticate import authenticate_cookie

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
    if verify_hash(password, user.password):
        access_token = create_access_token(user.id)
        return {"access_token": access_token, "token_type": "Bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )

#получение списка всех юзеров
@user_route.get('/all_users', response_model=List[User])
async def get_all_users_route(session=Depends(get_session)) -> list:
    return get_all_users(session)

#получение списка всех запросов
@user_route.get('/all_his', response_model=List[Task])
async def get_all_users_his(session=Depends(get_session)) -> list:
    return get_all_his(session)

#получение списка всех transaction
@user_route.get('/all_tr', response_model=List[Transaction])
async def get_all_users_tr(session=Depends(get_session)) -> list:
    return get_all_tr(session)

#получение баланса юзера по id
@user_route.get('/balance/', response_model=float)
async def get_balance_user(token: str, session=Depends(get_session)) -> float:
    user_id = int(await authenticate_cookie(token))
    balance = get_balance(user_id, session)
    return balance

#пополнение баланса
@user_route.post('/add_coin/')
async def add_coin(token: str,
                      amount: float,
                      session=Depends(get_session)):
    user_id = int(await authenticate_cookie(token))
    add_to_balance(user_id, amount, session)
    return {"message": "Coin added to user"}

#уменьшение баланса
@user_route.put('/deduct_coin/{user_id}')
async def deduct_coin(user_id: int,
                      amount: float,
                      session=Depends(get_session)):
    deduct_from_balance(user_id, amount, session)
    return {"message": f"Coin deduct from user (id {user_id})"}

#запрос истории транзакций юзера
@user_route.get('/transactions/{token}', response_model=List[Transaction])
async def get_transactions(token: str, session=Depends(get_session)):
    user_id = int(await authenticate_cookie(token))
    return tr_history(user_id, session)

#запрос имени
@user_route.get('/name/')
async def get_transactions(token: str, session=Depends(get_session)):
    user_id = int(await authenticate_cookie(token))
    return get_username(user_id, session)

# #запрос истории задач от юзера
# @user_route.get('/user_history/{user_id}')
# async def get_history(user_id: int, session=Depends(get_session)):
#     return task_history(user_id, session)






