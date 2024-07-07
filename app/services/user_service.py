from app.models.user import User
from typing import List, Optional
from pydantic import ValidationError
from datetime import datetime


def create_user(username: str, email: str, password: str, session):
    is_exist = session.query(User).where(User.username == username).first()
    if is_exist is not None:
        return {'Ошибка: Пользователь с таким логином уже существует'}

    # Запись нового пользователя
    password_hash = hash(password)
    new_user = User(username=username,
                    email=email,
                    password_hash=password_hash)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {'Успешное создание'}


def get_all_users(session) -> List[User]:
    """Возврат списка всех пользователей"""
    return session.query(User).all()



