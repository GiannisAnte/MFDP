from models.user import User
from models.transaction import Transaction
from services.transaction_service import transaction_log
from typing import List, Optional
from pydantic import ValidationError
from datetime import datetime
from models.balance import Balance


def create_user(username: str, email: str, password: str, session):
    is_exist_name = session.query(User).filter_by(username=username).first()
    is_exist_email = session.query(User).filter_by(email=email).first()
    if is_exist_name is not None or is_exist_email is not None:
        return {'Error: User already exists'}

    # Запись нового пользователя
    password = hash(password)# хэширование
    new_user = User(username=username,
                    email=email,
                    password=password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    #получение имени уже созданного юзера и создание его баланса
    user_id = get_user_by_username(username, session).id
    user_balance = Balance(user_id=user_id, user_balance=20)
    session.add(user_balance)
    session.commit()
    session.refresh(user_balance)
    return {"message": "User successfully registered!"}


def get_all_users(session) -> List[User]:
    """Возврат списка всех пользователей"""
    return session.query(User).all()

def get_user(user_id: int, session) -> Optional[User]:
    """Возврат юзера, если он существует"""
    user = session.query(User).where(User.id == user_id).first()
    return user

def get_user_by_username(username: str, session) -> Optional[User]:
    """Возврат юзера, если он существует"""
    user = session.query(User).where(User.username == username).first()
    return user

def authenticate(username: str, password: str, session) -> bool:
    """Пара login-password"""
    user = session.query(User).where(User.username == username).first()
    if int(user.password) == int(hash(password)):
        return True
    else:
        return False
# Старые методы, когда класс user столбец balance  
# def add_to_balance(user_id: int, amount: float, session) -> None:
#     """Увеличение баланса юзера"""
#     user = get_user(user_id, session)
#     new_transaction = Transaction(user_id=user_id,
#                             amount=amount,
#                             transaction_type='add')
#     transaction_log(new_transaction, session)
#     user.balance += amount
#     session.add(user, new_transaction)
#     session.commit()
#     session.refresh(user, new_transaction)


# def get_balance(user_id: int, session) -> float:
#     """Возврат баланса юзера"""
#     user = get_user(user_id, session)
#     return user.balance

# def deduct_from_balance(user_id: int, amount: float, session) -> None:
#     """Уменьшение баланса юзера"""
#     user = get_user(user_id, session)
#     new_transaction = Transaction(user_id=user_id,
#                             amount=amount,
#                             transaction_type='deduct')
#     transaction_log(new_transaction, session)
#     user.balance -= amount
#     session.add(user)
#     session.commit()
#     session.refresh(user)







