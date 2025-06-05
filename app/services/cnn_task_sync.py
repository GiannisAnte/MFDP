import base64
import uuid
from uuid import UUID
from pathlib import Path
from celery import shared_task
from sqlmodel import Session
from worker.tasks import process_cnn_data_task
from repository.fire_event_db import create_fire_event
from repository.predict_db import create_predict_event
from database.database import create_session
from worker.celery_app import celery_app
from services.user_service import get_user


IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def enqueue_cnn_task_sync(image_bytes: bytes, filename: str, content_type: str, session: Session, user_id: UUID) -> str:
    """
    1. Сохраняет file на диск
    2. Создаёт fire_event + prediction
    3. Коммитит одну транзакцию
    4. Кодирует base64
    5. Запускает task.delay
    Возвращает event_id
    """
    user = get_user(user_id, session)
    if not user:
        raise ValueError(f"User {user_id} not found")

    event_id = uuid.uuid4() #str(
    ext = Path(filename).suffix
    target = IMAGE_DIR / f"{event_id}{ext}"
    target.write_bytes(image_bytes)

    #fire_event и prediction
    create_fire_event(session=session,
        created_by=user_id,             
        source="satellite",
        event_id=event_id,
        payload={
            "image_path": str(target),
            "original_filename": filename,
            "mime_type": content_type
        })
    create_predict_event(session, event_id, status="PENDING", model_type="cnn")

    #Коммитим сразу обе
    session.commit()

    #шлём в Celery
    encoded = base64.b64encode(image_bytes).decode()
    task = process_cnn_data_task.delay(encoded, event_id, True)#run_cnn_prediction.delay(event_id, encoded, True)

    return event_id
