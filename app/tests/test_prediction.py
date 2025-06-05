from uuid import uuid4
from sqlmodel import select
from datetime import datetime

from models.fire_event import FireEvent
from models.prediction import Prediction
from models.user import User


def test_create_and_fetch_prediction(session):
    """
    Проверка создания и извлечения предсказания.
    """
    fire_event = FireEvent(
        source="satellite",
        latitude=10.0,
        longitude=20.0
    )
    session.add(fire_event)
    session.commit()
    session.refresh(fire_event)

    prediction = Prediction(
        fire_event_id=fire_event.id,
        model_type="cnn",
        variant="high_recall",
        result="wildfire",
        score=0.87,
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    #извлекается одно предсказание и все поля соответствуют
    results = session.exec(select(Prediction)).all()
    assert len(results) == 1

    p = results[0]
    assert p.fire_event_id == fire_event.id
    assert p.model_type == "cnn"
    assert p.variant == "high_recall"
    assert p.result == "wildfire"
    assert p.score == 0.87
    assert p.status == "pending"  # default
    assert isinstance(p.created_at, datetime)


def test_user_fireevent_prediction_relationship(session):
    """
    Проверяет связи:
        User -> FireEvent -> Prediction
    """

    # Создаем пользователя
    user = User(
        id=uuid4(),
        username="user",
        email="u@ue.com",
        hashed_password="1234a",
        is_superuser=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Создаем FireEvent, связанный с пользователем
    event = FireEvent(
        id=uuid4(),
        created_by=user.id,
        user=user,
        source="meteo",
        timestamp=datetime.utcnow(),
        latitude=55.75,
        longitude=37.61,
        payload={"path": 'path'}
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    # Создаем Prediction, связанный с FireEvent
    prediction = Prediction(
        id=uuid4(),
        fire_event_id=event.id,
        status="success",
        model_type="cnn",
        variant="balanced",
        result="wildfire",
        score=0.87,
        created_at=datetime.utcnow()
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    # Проверяем связи
    assert prediction.fire_event.id == event.id
    # assert prediction.fire_event.user.id == user.id
    assert event.predictions[0].id == prediction.id
    assert user.fire_events[0].id == event.id
