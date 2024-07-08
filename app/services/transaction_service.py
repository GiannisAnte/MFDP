from models.transaction import Transaction


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



