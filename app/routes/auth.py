from fastapi import APIRouter, Depends
from  database.database import get_session
from auth.authenticate import authenticate_cookie

auth_router = APIRouter(tags=['ML'])


@auth_router.get("/auth/{token}")
async def auth(token: str):
    result = await authenticate_cookie(token)
    return result
