from uuid import UUID, uuid4
from sqlmodel import Session
from services.user_service import get_user
from repository.fire_event_db import create_fire_event
from repository.predict_db import create_predict_event
from worker.tasks import process_weather_task
from schemas.WeatherRequest import WeatherRequest


def enqueue_weather_task_sync(req: WeatherRequest, session: Session) -> UUID:
    """
    1) Проверяет пользователя.
    2) Создаёт fire_event и prediction.
    3) Коммитит транзакцию.
    4) Ставит process_weather_task.delay(...)
    Возвращает event_id.
    """
    user = get_user(req.user_id, session)
    if not user:
        raise ValueError(f"User {req.user_id} not found")

    event_id = uuid4()

    # 2) Сохраняем fire_event и prediction
    create_fire_event(
        session=session,
        created_by=req.user_id,
        source="weather_api",
        event_id=event_id,
        payload={
            "date": req.date,
            "forecast": req.forecast,
            "customer": req.customer
        },
        latitude=req.latitude,
        longitude=req.longitude
    )
    create_predict_event(
        session=session,
        event_id=event_id,
        status="PENDING",
        model_type=req.customer
    )

    session.commit()

    # 4) Ставим Celery-задачу
    process_weather_task.delay(
        str(event_id),
        req.latitude,
        req.longitude,
        req.date,
        req.forecast,
        req.customer
    )

    return event_id