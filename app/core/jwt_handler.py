from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import jwt, JWTError
from database.config import get_settings  # исправлено

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

def create_access_token(user: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": user,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
