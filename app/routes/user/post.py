from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from services.user_service import create_user, get_user_by_username
from services.balance_servise import add_to_balance
from auth.hash_password import verify_hash
from auth.jwt_handler import create_access_token
from auth.authenticate import authenticate_cookie
from pydantic import EmailStr

post_user_route = APIRouter(tags=['User'])


@post_user_route.post('/signup')
async def signup(username: str, email: EmailStr, password: str, session=Depends(get_session)):
    '''Регистрация юзера'''
    response = create_user(username, email, password, session)
    if response == {'Error: User already exists'}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already exists")
    if response == {"message": "User successfully registered!"}:
        return {"message": "User successfully registered!"}


@post_user_route.post('/signin')
async def signin(username: str, password: str, session=Depends(get_session)):
    '''Авторизация и аутентификация'''
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


@post_user_route.post('/coin/')
async def add_coin(token: str,
                      amount: float,
                      session=Depends(get_session)):
    '''Пополнение баланса'''
    user_id = int(await authenticate_cookie(token))
    add_to_balance(user_id, amount, session)
    return {"message": "Coin added to user"}

@post_user_route.post('/coins/{user_id}')
async def add_coins(user_id: int,
                      amount: float,
                      session=Depends(get_session)):
    '''Ппополние баланса по id, сервисный ендпоинт'''
    add_to_balance(user_id, amount, session)
    return {"message": f"Coin added"}

# Основные правила валидации EmailStr:

# * Должен содержать символ "@": Это обязательное условие, без него строка не будет считаться email-адресом.
# * Должен содержать хотя бы одно имя домена:  Часть после "@" должна быть непустой и включать хотя бы один домен. Например, "example.com".
# * Должен содержать хотя бы один поддомен: После "@" должна быть хотя бы одна точка (".") для разделения поддомена. Например, "google.com".
# * Допускается использование цифр, букв и некоторых символов:  В имени пользователя и в поддомене допускаются цифры, буквы, дефис (-) и точка (.).  
# * Не допускаются недопустимые символы:  Не допускаются специальные символы (например, $, %, &, т. д.) в начале и конце email-адреса.  
