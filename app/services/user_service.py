from models.user import User
from models.transaction import Transaction
from services.transaction_service import transaction_log
from typing import List, Optional
from pydantic import ValidationError
from datetime import datetime


def create_user(username: str, email: str, password: str, session):
    is_exist = session.query(User).filter_by(username=username).first()
    if is_exist is not None:
        return {'Ошибка: Пользователь с таким логином уже существует'}

    # Запись нового пользователя
    password = hash(password)# хэширование
    new_user = User(username=username,
                    email=email,
                    password=password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {'Успешное создание'}


def get_all_users(session) -> List[User]:
    """Возврат списка всех пользователей"""
    return session.query(User).all()

def get_user(user_id: int, session) -> Optional[User]:
    """Возврат юзера, если он существует"""
    user = session.query(User).where(User.id == user_id).first()
    return user


def authenticate(username: str, password: str, session) -> bool:
    """Пара login-password"""
    user = session.query(User).where(User.username == username).first()
    if int(user.password) == int(hash(password)):
        return True
    else:
        return False
    
def add_to_balance(user_id: int, amount: float, session) -> None:
    """Увеличение баланса юзера"""
    user = get_user(user_id, session)
    new_transaction = Transaction(user_id=user_id,
                            amount=amount,
                            transaction_type='add')
    transaction_log(new_transaction, session)
    user.balance += amount
    session.add(user, new_transaction)
    session.commit()
    session.refresh(user, new_transaction)


def get_balance(user_id: int, session) -> float:
    """Возврат баланса юзера"""
    user = get_user(user_id, session)
    return user.balance

def deduct_from_balance(user_id: int, amount: float, session) -> None:
    """Уменьшение баланса юзера"""
    user = get_user(user_id, session)
    new_transaction = Transaction(user_id=user_id,
                            amount=amount,
                            transaction_type='deduct')
    transaction_log(new_transaction, session)
    user.balance -= amount
    session.add(user)
    session.commit()
    session.refresh(user)







