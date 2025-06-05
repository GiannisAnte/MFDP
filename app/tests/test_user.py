import pytest
from sqlmodel import Session, select
from uuid import UUID
from models.user import User


def test_create_user(session: Session):
    """
    Тест: создание пользователя с валидными данными
    """
    #Создаём
    user = User(
        username="test",
        email="test@mail.ru",
        hashed_password="password_123",
        is_superuser=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    #Проверяем, что поля заполнены
    assert isinstance(user.id, UUID)
    assert user.username == "test"
    assert user.email == "test@mail.ru"
    assert user.hashed_password == "password_123"
    assert user.is_superuser is False
    assert user.created_at is not None

    #Проверка, что в БД ровно один пользователь
    users_after = session.exec(select(User)).all()
    assert len(users_after) == 1
    assert users_after[0].id == user.id


def test_fail_create_user_duplicate_email(session: Session):
    """
    Тест: при попытке создать двух пользователей с одинаковым email
    должно возникать исключение (из-за unique-ограничения).
    """
    user1 = User(
        username="user1",
        email="a@mail.ru",
        hashed_password="password1"
    )
    session.add(user1)
    session.commit()

    user2 = User(
        username="user2",
        email="a@mail.ru",
        hashed_password="password2"
    )
    session.add(user2)
    with pytest.raises(Exception) as excinfo:
        session.commit()
    msg = str(excinfo.value).lower()
    assert "unique" in msg or "constraint" in msg or "email" in msg
    session.rollback()


def test_delete_user(session: Session):
    """
    Тест: удаление пользователя.
    Создаём пользователя, затем удаляем и убеждаемся, что его больше нет в БД.
    """
    user = User(
        username="user3",
        email="a@mail.ru",
        hashed_password="some_password"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    fetched = session.get(User, user.id)
    assert fetched is not None
    assert fetched.email == "a@mail.ru"

    session.delete(fetched)
    session.commit()

    deleted = session.get(User, user.id)
    assert deleted is None


def test_list_users_and_fields(session: Session):
    """
    Тест: добавляем несколько пользователей и проверяем, что
    при выборке через select(User) возвращается полный список
    с корректно заполненными полями.
    """
    #Предварительно база пуста
    assert session.exec(select(User)).all() == []

    u1 = User(username="a1", email="a1@mail.ru", hashed_password="aaa")
    u2 = User(username="a2", email="a2@mail.ru", hashed_password="bbb", is_superuser=True)
    session.add_all([u1, u2])
    session.commit()
    session.refresh(u1)
    session.refresh(u2)


    all_users = session.exec(select(User)).all()
    #Ожидаем 2 записи
    assert len(all_users) == 2

    #Проверка, что у каждого поля правильные значения
    emails = {u.email for u in all_users}
    assert emails == {"a1@mail.ru", "a2@mail.ru"}

    usernames = {u.username for u in all_users}
    assert usernames == {"a1", "a2"}

    #Проверяем, что у a2 выставлен флаг is_superuser=True
    bob = next(u for u in all_users if u.username == "a2")
    assert bob.is_superuser is True

    # поле created_at
    for u in all_users:
        assert u.created_at is not None

