from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from services.user_service import create_user, get_user_by_username
from core.hash_password import HashPassword#verify_hash
from core.jwt_handler import create_access_token
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from fastapi import Response
from database.config import get_settings

settings = get_settings()


post_user_route = APIRouter(tags=['User'])

hash_password = HashPassword()

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
async def signin(username: str, password: str, response: Response, session=Depends(get_session)):
    '''Авторизация и установка JWT в cookie'''
    user = get_user_by_username(username, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if hash_password.verify_hash(password, user.hashed_password):
        access_token = create_access_token(str(user.id))
        # Устанавливаем токен в cookie с параметрами безопасности
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=False,          # ставь True если HTTPS, иначе False
            samesite="lax",       # или "strict" в зависимости от требований
            max_age=3600          # время жизни cookie в секундах (1 час)
        )
        return {"access_token": access_token, "message": "Login successful"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials."
    )



# Основные правила валидации EmailStr:

# * Должен содержать символ "@": Это обязательное условие, без него строка не будет считаться email-адресом.
# * Должен содержать хотя бы одно имя домена:  Часть после "@" должна быть непустой и включать хотя бы один домен. Например, "example.com".
# * Должен содержать хотя бы один поддомен: После "@" должна быть хотя бы одна точка (".") для разделения поддомена. Например, "google.com".
# * Допускается использование цифр, букв и некоторых символов:  В имени пользователя и в поддомене допускаются цифры, буквы, дефис (-) и точка (.).  
# * Не допускаются недопустимые символы:  Не допускаются специальные символы (например, $, %, &, т. д.) в начале и конце email-адреса.  
