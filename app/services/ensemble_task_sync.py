import base64
import uuid
from uuid import UUID
from pathlib import Path
from celery import shared_task
from sqlmodel import Session
from typing import Optional
from uuid import UUID, uuid4
from datetime import date
from services.user_service import get_user
from repository.fire_event_db import create_fire_event
from repository.predict_db import create_predict_event
from worker.tasks import process_ensemble_task


IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def enqueue_ensemble_task_sync(
    image_bytes: bytes,
    filename: str,
    content_type: str,
    lat: float,
    lon: float,
    target_date: Optional[date],
    forecast: Optional[int],
    customer: str,
    alpha: float,
    session: Session,
    user_id: UUID
) -> UUID:
    """
    1. Проверяем, что пользователь существует.
    2. Сохраняем файл на диск (в IMAGE_DIR).
    3. Создаём fire_event и prediction со статусом PENDING и model_type="ensemble".
    4. Коммитим одну транзакцию.
    5. Кодируем изображение в base64 и ставим Celery-таск process_ensemble_task.delay(...).
    Возвращаем event_id.
    """
    # 1) Проверяем пользователя
    user = get_user(user_id, session)
    if not user:
        raise ValueError(f"User {user_id} not found")

    # 2) Сохраняем файл во временную папку
    event_id = uuid4()
    ext = Path(filename).suffix
    target_path = IMAGE_DIR / f"{event_id}{ext}"
    target_path.write_bytes(image_bytes)

    # 3) Создаём fire_event + prediction
    payload = {
        "image_path": str(target_path),
        "original_filename": filename,
        "mime_type": content_type,
        "latitude": lat,
        "longitude": lon,
        "date": target_date.isoformat() if target_date else None,
        "forecast": forecast,
        "customer": customer,
        "alpha": alpha
    }
    create_fire_event(
        session=session,
        created_by=user_id,
        source="ensemble_api",
        event_id=event_id,
        payload=payload,
        latitude=lat,
        longitude=lon
    )
    create_predict_event(
        session=session,
        event_id=event_id,
        status="PENDING",
        model_type="ensemble"
    )

    # 4) Коммитим fire_event и prediction
    session.commit()

    # 5) Шлём в Celery: кодируем изображение в base64
    encoded_image = base64.b64encode(image_bytes).decode()
    process_ensemble_task.delay(
        str(event_id),
        encoded_image,
        lat,
        lon,
        target_date.isoformat() if target_date else None,
        forecast,
        customer,
        alpha
    )

    return event_id