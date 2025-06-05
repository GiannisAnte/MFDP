from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from pathlib import Path
from uuid import UUID
from database.database import get_session
from worker.celery_app import celery_app
import logging
from worker.celery_app import celery_app
from celery.result import AsyncResult
from anyio import to_thread
from services.cnn_task_sync import enqueue_cnn_task_sync
from typing import Optional
from datetime import date
from services.daily_weather import get_daily_weather
from schemas.WeatherRequest import WeatherRequest
from services.weather_task_sync import enqueue_weather_task_sync
from services.ensemble_task_sync import enqueue_ensemble_task_sync
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router_cnn = APIRouter(tags=['ML'])
router_ml = APIRouter(tags=['ML'])
router_w = APIRouter(tags=['ML'])

IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

@router_cnn.post("/predict/cnn/")
async def upload_image_and_enqueue_cnn_task(
    user_id: UUID,
    file: UploadFile = File(...),
    session = Depends(get_session)
):
    try:
        image_bytes = await file.read()

        event_id = await to_thread.run_sync(
            enqueue_cnn_task_sync,
            image_bytes,
            file.filename,
            file.content_type,
            session,
            user_id
        )
        return {"event_id": event_id}
    except ValueError as ve:
        # Если пользователь не найден
        raise HTTPException(status_code=404, detail=str(ve))    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_ml.post("/weather/predict")
async def enqueue_weather_predict(
    req: WeatherRequest,
    session = Depends(get_session)
):
    """
    Принимает JSON с user_id, latitude, longitude, date/forecast и заказчика (customer).
    Сохраняет fire_event + prediction (status="PENDING"), затем ставит Celery-задачу.
    """
    try:
        event_id = await run_in_threadpool(
            enqueue_weather_task_sync,
            req,
            session
        )
        return event_id
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_ml.post("/predict/ensemble/")
async def upload_and_enqueue_ensemble(
    user_id: UUID,
    file: UploadFile = File(...),
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    target_date: Optional[date] = Query(None, description="Дата (YYYY-MM-DD)"),
    forecast: Optional[int] = Query(None, description="Смещение в днях от сегодня"),
    customer: str = Query(..., description="Имя табличной модели: cb_xgb или cb_rf"),
    alpha: float = Query(0.5, ge=0.0, le=1.0, description="Вес табличной модели α (по умолчанию 0.5)"),
    session = Depends(get_session)
):
    """
    1. Читает изображение из `file`.
    2. Передаёт все входные параметры + alpha в sync‐функцию enqueue_ensemble_task_sync через run_in_threadpool.
    3. Возвращает {"event_id": <UUID>}.
    """
    try:
        image_bytes = await file.read()
        event_id = await run_in_threadpool(
            enqueue_ensemble_task_sync,
            image_bytes,
            file.filename,
            file.content_type,
            lat,
            lon,
            target_date,
            forecast,
            customer,
            alpha,
            session,
            user_id
        )
        return {"event_id": event_id}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_w.get("/weather")
def get_weather(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    target_date: Optional[date] = Query(None, description="Конкретная дата (yyyy-mm-dd)"),
    forecast: Optional[int] = Query(None, description="Смещение в днях от текущей даты")
):
    """
    Получение данных о погоде на указанный день или смещенный относительно текущего.
    """
    try:
        weather = get_daily_weather(latitude=lat, longitude=lon, date=target_date, forecast=forecast)
        return weather
    except Exception as e:
        return {"error": str(e)}

# @router_cnn.post("/predict/cnn/")
# def upload_image_and_enqueue_cnn_task(file: UploadFile = File(...),
#     session = Depends(get_session)):
#     try:
#         with file.file as f:
#             image_bytes = f.read()
#         encoded_img = base64.b64encode(image_bytes).decode()

#         event_id = str(uuid.uuid4())

#         extension = Path(file.filename).suffix
#         filename = f"{event_id}{extension}"
#         file_path = IMAGE_DIR / filename

#         with open(file_path, "wb") as buffer:
#             buffer.write(image_bytes)

#         payload = {
#             "image_path": str(file_path),
#             "original_filename": file.filename,
#             "mime_type": file.content_type
#         }

#         create_fire_event(
#             session=session,
#             event_id=event_id,
#             source="satellite",
#             payload=payload
#         )

#         create_predict_event(
#             session=session,
#             event_id=event_id,
#             status="PENDING",
#             model_type="cnn"
#         )

#         session.commit()

#         task = process_cnn_data_task.delay(encoded_img, event_id, True)
#         logger.info(f"Celery broker URL: {celery_app.conf.broker_url}")
#         logger.info(f"Celery result backend: {celery_app.conf.result_backend}")
#         logger.info(f"Task backend via task.app: {process_cnn_data_task.app.conf.result_backend}")

#         return {"message": "Task completed", "task_id": task.id}
#     except Exception as e:
#         logger.error(f"[CNN TASK] Error processing the image: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @router_cnn.post("/predict/cnn")
# async def predict_cnn_endpoint(file: UploadFile = File(...)):
#     if file.content_type not in ["image/jpeg", "image/png"]:
#         raise HTTPException(status_code=400, detail="Only JPEG or PNG images")
    
#     try:
#         image_bytes = await file.read()
#         image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#         prediction = predict_cnn(image)
#         return prediction
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

#Старая версия 
# @router_cnn.post("/predict/cnn/")
# async def upload_image_and_enqueue_cnn_task(
#     file: UploadFile = File(...),
#     session = Depends(get_session)
# ):
#     try:
#         image_bytes = await file.read()
#         encoded_img = base64.b64encode(image_bytes).decode()

#         event_id = str(uuid.uuid4())
#         extension = Path(file.filename).suffix
#         filename = f"{event_id}{extension}"
#         file_path = IMAGE_DIR / filename
#         file_path.write_bytes(image_bytes)

#         # 1) Создаём fire_event
#         create_fire_event(
#             session=session,
#             event_id=event_id,
#             source="satellite",
#             payload={
#                 "image_path": str(file_path),
#                 "original_filename": file.filename,
#                 "mime_type": file.content_type
#             }
#         )
        
#         create_predict_event(
#             session=session,
#             event_id=event_id,
#             status="PENDING",
#             model_type="cnn"
#         )

#         # 3) Отправляем задачу в Celery
#         task = process_cnn_data_task.delay(event_id, encoded_img, True)
#         logger.info(f"Enqueued Celery task {task.id} for event {event_id}")

#         return {"task_id": event_id}

#     except Exception as e:
#         logger.error(f"[CNN TASK] Error enqueueing task: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")