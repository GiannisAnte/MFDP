from models.transaction import Transaction
from models.user import User
from shema.Transactions import Transactions
from typing import List
from sqlalchemy import join
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def transaction_log(transaction: Transaction, session) -> None:
    """Запись транзакци в БД"""
    session.add(transaction)
    session.commit()
    session.refresh(transaction)


def tr_history(user_id: int, session) -> list[Transaction]:
    """История транзакций юзера"""
    trans_history = (session.query(Transaction)
                     .where(Transaction.user_id == user_id)
                     .all())
    return trans_history


def get_all_tr(session) -> List[Transactions]:
    """Возврат запросов всех пользователей, тут мы объединяем две таблицы, 
    чтобы плюсом получить имя юзера из одноименной таблицы"""
    # return session.query(Transaction).all()
    transactions = (
    session.query(User, Transaction)
    .join(Transaction, User.id == Transaction.user_id)
    .all()
    )

    transaction_data = []
    for user, transaction in transactions:
        transaction_data.append({
        'id транзакции': transaction.transaction_id,
        'id юзера': transaction.user_id,
        'имя юзера': user.username,
        'тип транзакции': transaction.transaction_type,
        'количество': transaction.amount,
    })

    return JSONResponse(content=jsonable_encoder(transaction_data))



