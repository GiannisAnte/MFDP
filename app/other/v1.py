

#database

# from sqlmodel import SQLModel, Session, create_engine
# from sqlalchemy.orm import sessionmaker
# from database.config import get_settings
# from models.user import User
# from models.fire_event import FireEvent
# from models.prediction import Prediction
# from core.hash_password import create_hash
# import os
# from dotenv import load_dotenv

# env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))
# load_dotenv(env_path)

# engine = create_engine(url=get_settings().DATABASE_URL_psycopg2,
#                        echo=False, pool_size=5, max_overflow=10)

# # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_session():
#     with Session(engine) as session:
#         yield session

# def create_session() -> Session:
#     return Session(engine)


# def create_superuser():
#     with Session(engine) as session:
#         # Проверка: есть ли уже админ
#         existing_admin = session.query(User).filter_by(is_superuser=True).first()
#         if not existing_admin:
#             admin_user = User(
#                 username="admin",
#                 email="admin@example.com",
#                 hashed_password=create_hash(os.getenv("ADMIN_PASSWORD")),
#                 is_superuser=True
#             )
#             session.add(admin_user)
#             session.commit()
#             print("Администратор создан")

# def init_db():
#     """Инициализация базы данных"""
#     SQLModel.metadata.drop_all(engine)
#     SQLModel.metadata.create_all(engine)
#     create_superuser()

#prediction_cnn

# import torch
# from PIL import Image
# from torchvision import transforms
# import torch.nn.functional as F
# from sqlmodel import Session
# import logging
# from ml.core.cnn_model import get_model
# from models.prediction import Prediction


# logger = logging.getLogger(__name__)


# transform = transforms.Compose([
#     transforms.Resize((32, 32)),
#     transforms.ToTensor(),
#     transforms.Normalize([0.5]*3, [0.5]*3)
# ])

# def predict_cnn(image: Image.Image) -> dict:
#     input_tensor = transform(image).unsqueeze(0) 

#     with torch.no_grad():
#         model = get_model()
#         output = model(input_tensor)
#         probs = F.softmax(output, dim=1)
#         confidence, pred_class = torch.max(probs, 1)
#         class_names = ['nowildfire', 'wildfire']
#         predicted_label = class_names[pred_class.item()]
#         confidence_pct = confidence.item() * 100

#     return {"predicted_label": predicted_label, "confidence_pct": f"{confidence_pct:.2f}%"}


# def run_cnn_prediction(image: Image.Image, event_id: str, session: Session) -> Prediction:
#     result = predict_cnn(image)

#     rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
#     if not rec:
#         raise ValueError(f"Prediction not found for event_id={event_id}")
    
#     logger.info("Before update: %s", rec.to_dict())

#     rec.status = 'SUCCESS'
#     rec.variant = 'CNN'
#     rec.score =  result.get('confidence_pct', 'None').replace('%', '').strip()
#     rec.result = result.get('predicted_label')

#     return rec

#tasks

# import base64
# import logging
# from io import BytesIO
# from uuid import UUID
# from PIL import Image
# import time
# import random
# from celery import shared_task
# from sqlmodel import Session
# from io import BytesIO
# from worker.celery_app import celery_app
# from services.predict_cnn import predict_cnn, run_cnn_prediction
# # from database.database import SessionLocal
# from database.database import engine, create_session


# logger = logging.getLogger(__name__)


# @shared_task
# def test_task(name):
#     delay = random.randint(1, 5)
#     print(f"[{name}] Sleeping for {delay} seconds...")
#     time.sleep(delay)
#     print(f"[{name}] Done sleeping.")
#     return f"Finished {name}"


# @shared_task
# def process_cnn_data_task(image_input: str, event_id: str, is_base64: bool = True) -> dict:
#     # session = SessionLocal()
#     with create_session() as session:
#         try:
#             if is_base64:
#                 image_data = base64.b64decode(image_input)
#                 image = Image.open(BytesIO(image_data)).convert("RGB")
#             else:
#                 image = Image.open(image_input).convert("RGB")
#         except Exception as e:
#             return {"error": f"Failed to load image: {e}"}
        
#         try:
#             rec = run_cnn_prediction(image, event_id, session) #логику унес в отдельную функцию
#             session.commit()
#             logger.info("After update: %s", rec.to_dict())
#             return {"predicted_label": rec.result, "confidence_pct": rec.score}
#         except Exception as e:
#             session.rollback()
#             return {"error": str(e)}

#         # rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
#         # if not rec:
#         #     logger.error(f"No Prediction found for event_id={event_id}")
#         #     return {"error": "Prediction record not found"}

#         # logger.info("Before update: %s", rec.to_dict())

#         # rec.status = 'SUCCESS'
#         # rec.variant = 'CNN'
#         # rec.score = float(str(result.get('confidence_pct')).rstrip('%'))
#         # rec.result = result.get('predicted_label')

#         # session.commit()

#         # logger.info("After update: %s", rec.to_dict())

#         # return {"predicted_label": rec.result, "confidence_pct": rec.score}


# # @shared_task
# # def process_cnn_data_task(image_bytes_b64: str, event_id: str):
# #     image_bytes = base64.b64decode(image_bytes_b64)
# #     image = Image.open(BytesIO(image_bytes)).convert("RGB")

# #     result = predict_cnn(image)

# #     print(f"[CNN TASK] Event ID: {event_id} — Result: {result}")

# #     return result

# #Старая версия
# # @shared_task
# # def process_cnn_data_task(image_input: str, event_id: str, is_base64: bool = True) -> dict:
# #     session = SessionLocal()
# #     try:
# #         if is_base64:
# #             image_data = base64.b64decode(image_input)
# #             image = Image.open(BytesIO(image_data)).convert("RGB")
# #         else:
# #             image = Image.open(image_input).convert("RGB")
# #     except Exception as e:
# #         return {"error": f"Failed to load image: {e}"}
    
# #     result = predict_cnn(image)

# #     rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
# #     if rec:
# #         logger.info("Before update: %s", rec.to_dict())

# #         rec.status = 'SUCCESS'
# #         rec.variant = result.get('predicted_label')
# #         rec.score = float(str(result.get('confidence_pct')).rstrip('%'))
# #         rec.result = result.get('predicted_label')  # или str(result), если нужно всё

# #         session.add(rec)  # <= на всякий случай
# #         session.commit()

# #         logger.info("After update: %s", rec.to_dict())

# #     return result.get('predicted_label')

# router_cnn

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

#fire_event_db

# def create_fire_event(
#     # session: get_session,
#     session: Session,
#     source: str,
#     event_id: UUID,
#     payload: dict= None,
#     latitude: float = None,
#     longitude: float = None,
# ) -> FireEvent:
#     fe = FireEvent(
#         id=event_id,
#         source=source,
#         timestamp=datetime.utcnow(),
#         latitude=latitude,
#         longitude=longitude,
#         payload=payload,
#     )
#     session.add(fe)
#     # session.commit()
#     # session.refresh(fe) делаю общий коммит в роуте
#     return fe




# @router_w.get("/weather")
# def get_weather(
#     lat: float = Query(..., description="Широта"),
#     lon: float = Query(..., description="Долгота"),
#     target_date: Optional[date] = Query(None, description="Конкретная дата (yyyy-mm-dd)"),
#     forecast: Optional[int] = Query(None, description="Смещение в днях от текущей даты")
# ):
#     """
#     Получение данных о погоде на указанный день или смещенный относительно текущего.
#     """
#     try:
#         weather = get_daily_weather(latitude=lat, longitude=lon, date=target_date, forecast=forecast)
#         # return weather
#     except Exception as e:
#         return {"error": str(e)}
#     try:
#         model = joblib.load('ml/stacking_cb_rf_model')#stacking_xgb_cb_model

#         features = {
#             str(feat): weather[str(feat)]
#             for feat in model.feature_names_in_
#         }

#         # Создаём DataFrame с одной строкой и нужными колонками
#         df = pd.DataFrame([features], columns=model.feature_names_in_)

#         # Предсказание класса и вероятностей
#         proba = model.predict_proba(df)[0]
#         prob_positive = float(proba[1])
#         pred_class = 1 if prob_positive >= 0.172 else 0

#         confidence_str = f"{prob_positive * 100:.2f}%"
#         label_map = {0: "No Fire", 1: "Fire"}
#         pred_label = label_map[pred_class]

#         return {
#             "model_type": model.__class__.__name__,
#             "prediction": {
#                 "class": pred_class,
#                 "label": pred_label,
#                 "confidence": confidence_str
#             }
#         }


#     except Exception as e:
#         return {"error": str(e)}