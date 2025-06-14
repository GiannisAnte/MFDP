from fastapi import Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer
from core.jwt_handler import verify_access_token 
from core.cookieauth import OAuth2PasswordBearerWithCookie

# Авторизация через заголовок Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )
    decoded_token = verify_access_token(token)
    return decoded_token["sub"]

# Авторизация через cookie
oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/token")

async def authenticate_cookie(token: str = Depends(oauth2_scheme_cookie)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )
    decoded_token = verify_access_token(token)
    return decoded_token["sub"]
