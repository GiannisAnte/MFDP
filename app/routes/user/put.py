from fastapi import APIRouter, Depends
from database.database import get_session
from services.balance_servise import deduct_from_balance

put_user_route = APIRouter(tags=['User'])


@put_user_route.put('/deduct_coin/{user_id}')
async def deduct_coin(user_id: int,
                      amount: float,
                      session=Depends(get_session)):
    '''Уменьшение баланса'''
    deduct_from_balance(user_id, amount, session)
    return {"message": f"Coin deduct from user"}