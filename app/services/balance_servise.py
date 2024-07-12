from models.balance import Balance
from sqlalchemy.orm import Session
from models.transaction import Transaction
from services.transaction_service import transaction_log
from services.user_service import get_user


def add_to_balance(user_id: int, amount: float, session: Session) -> None:
    """Увеличение баланса юзера"""
    user = get_user(user_id, session)
    if user:
        user_balance = session.query(Balance).filter_by(user_id=user_id).first()
        new_transaction = Transaction(user_id=user_id,
                                amount=amount,
                                transaction_type='add')
        transaction_log(new_transaction, session)
        user_balance = session.query(Balance).filter_by(user_id=user_id).first()
        user_balance.user_balance += amount
        session.add(user_balance)
        session.add(user, new_transaction)
        session.commit()
        session.refresh(user, new_transaction)
        session.refresh(user_balance)
    else:
        print('User not found')


def get_balance(user_id: int, session: Session) -> float:
    """Возврат баланса юзера"""
    user = session.query(Balance).filter_by(user_id=user_id).first()
    return user.user_balance if user else 0.0


def deduct_from_balance(user_id: int, amount: float, session: Session) -> None:
    """Уменьшение баланса юзера"""
    user = get_user(user_id, session)
    if user:
        user_balance = session.query(Balance).filter_by(user_id=user_id).first()
        if user_balance.user_balance >= amount:
            new_transaction = Transaction(user_id=user_id,
                                    amount=amount,
                                    transaction_type='deduct')
            transaction_log(new_transaction, session)
            user_balance.user_balance -= amount
            session.add(user_balance)
            session.add(user, new_transaction)
            session.commit()
            session.refresh(user, new_transaction)
            session.refresh(user_balance)
        else:
            print('Balance less than amount')
    else:
        print('User not found')
       