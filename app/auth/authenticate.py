from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import verify_access_token
from services.auth.cookieauth import OAuth2PasswordBearerWithCookie


oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="token")


async def authenticate_cookie(token: str = Depends(oauth2_scheme_cookie)) -> str:
    """
    Аутентификация юзера по токену, возвращает id юзера
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in for access"
        )
    token = token.removeprefix("Bearer ")
    decoded_token = verify_access_token(token)
    return decoded_token["id"]
