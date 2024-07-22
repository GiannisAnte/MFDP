from models.transaction import Transaction
from typing import List

def transaction_log(transaction: Transaction, session) -> None:
    """Запись транзакци в БД"""
    session.add(transaction)
    session.commit()
    session.refresh(transaction)


def tr_history(user_id: int, session) -> list[Transaction]:
    """История транзакций"""
    trans_history = (session.query(Transaction)
                     .where(Transaction.user_id == user_id)
                     .all())
    return trans_history


def get_all_tr(session) -> List[Transaction]:
    """Возврат запросов всех пользователей"""
    return session.query(Transaction).all()



