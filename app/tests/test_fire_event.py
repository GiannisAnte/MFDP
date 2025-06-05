import pytest
from uuid import uuid4
from sqlmodel import select
from datetime import datetime

from models.user import User
from models.fire_event import FireEvent


def test_create_and_fetch_fire_event(session):
    """
    Проверка создания и выборки события пожара.
    """

    # Создаём пользователя
    user = User(username="user", email="user@u.com", hashed_password="123")
    session.add(user)
    session.commit()
    session.refresh(user)

    #Создаём FireEvent
    fire_event = FireEvent(
        created_by=user.id,
        source="satellite",
        latitude=55.7558,
        longitude=37.6176,
        payload={"path": 'path'}
    )
    session.add(fire_event)
    session.commit()
    session.refresh(fire_event)

    #Проверяем, что событие записалось и извлекается корректно
    result = session.exec(select(FireEvent)).all()
    assert len(result) == 1

    fetched_event = result[0]
    assert fetched_event.created_by == user.id
    assert fetched_event.source == "satellite"
    assert fetched_event.latitude == 55.7558
    assert fetched_event.longitude == 37.6176
    assert fetched_event.payload == {"path": 'path'}
    assert isinstance(fetched_event.timestamp, datetime)


def test_create_fire_event_without_coordinates(session):
    """
    Проверка, что можно создать событие пожара без координат.
    """
    fire_event = FireEvent(
        source="meteo",
        payload={"note": "GPS"},
    )
    session.add(fire_event)
    session.commit()

    result = session.exec(select(FireEvent)).first()
    assert result is not None
    assert result.latitude is None
    assert result.longitude is None
    assert result.source == "meteo"


def test_fire_event_user_relationship(session):
    """
    Проверка, что можно получить пользователя через FireEvent.user
    """
    user = User(username="user", email="u@u.com", hashed_password="123")
    session.add(user)
    session.commit()
    session.refresh(user)

    fire_event = FireEvent(
        created_by=user.id,
        source="meteo"
    )
    session.add(fire_event)
    session.commit()
    session.refresh(fire_event)

    # Проверка связи
    assert fire_event.user.id == user.id
    assert fire_event.user.email == "u@u.com"
