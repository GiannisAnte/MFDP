import base64
import logging
from io import BytesIO
from uuid import UUID
from PIL import Image
import time
import random
from typing import Optional
from celery import shared_task
from sqlmodel import Session
from io import BytesIO
from worker.celery_app import celery_app
from services.predict_cnn import predict_cnn, run_cnn_prediction
from services.daily_weather import get_daily_weather
from database.database import engine, create_session
from ml.core.table_models import get_model_and_threshold
from models.prediction import Prediction
import pandas as pd

logger = logging.getLogger(__name__)

LABEL_MAP = {0: "nowildfire", 1: "wildfire"}

LABEL_MAP_E = {
    0: "nowildfire",            # нет пожара
    1: "wildfire",              # природный пожар
    2: "anthropogenic_fire"     # антропогенный пожар
}


@shared_task
def test_task(name):
    delay = random.randint(1, 5)
    print(f"[{name}] Sleeping for {delay} seconds...")
    time.sleep(delay)
    print(f"[{name}] Done sleeping.")
    return f"Finished {name}"


@shared_task(
    name="worker.tasks.process_cnn_data_task",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    acks_late=True
)
def process_cnn_data_task(image_input: str, event_id: str, is_base64: bool = True) -> dict:
    # session = SessionLocal()
    with create_session() as session:
        try:
            if is_base64:
                image_data = base64.b64decode(image_input)
                image = Image.open(BytesIO(image_data)).convert("RGB")
            else:
                image = Image.open(image_input).convert("RGB")
        except Exception as e:
            return {"error": f"Failed to load image: {e}"}
        
        try:
            rec = run_cnn_prediction(image, event_id, session) #логику унес в отдельную функцию
            session.commit()
            logger.info("After update: %s", rec.to_dict())
            return {"predicted_label": rec.result, "confidence_pct": rec.score}
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        
@shared_task(
    name="worker.tasks.process_weather_task",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    acks_late=True
)
def process_weather_task(
    event_id: str,
    latitude: float,
    longitude: float,
    date: str,
    forecast: int,
    customer: str
) -> dict:
    """
    1) Получает погодные данные.
    2) Если «Невалидный день» → обновляет prediction.status="FAILED" и завершает.
    3) Иначе загружает модель + порог через get_model_and_threshold(customer).
    4) Формирует DataFrame для предсказания, вычисляет predict_proba, сравнивает с threshold.
    5) Обновляет prediction.status="SUCCESS", rec.result и rec.payload.
    """
    with create_session() as session:
        try:
            # 1) Получаем данные о погоде
            weather_data = get_daily_weather(
                latitude=latitude,
                longitude=longitude,
                date=date,
                forecast=forecast
            )

            # 2) Проверяем валидность
            if "Невалидный день" in weather_data:
                rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
                if rec:
                    rec.status = "FAILED"
                    missing = weather_data.get("Отсутствуют признаки")
                    if missing:
                        rec.result = 'Отсутствует часть признаков'
                    else:
                        rec.result = f'Невалидный день:{weather_data["Невалидный день"]}'
                session.commit()
                return {
                    "event_id": event_id,
                    "status": "FAILED",
                    "reason": weather_data["Невалидный день"]
                }

            # 3) Загружаем модель и порог
            model, threshold, description = get_model_and_threshold(customer)

            # 4) Собираем DataFrame для предсказания
            features = {
                str(feat): weather_data[str(feat)]
                for feat in model.feature_names_in_
            }
            df = pd.DataFrame([features], columns=model.feature_names_in_)

            # probs = model.predict_proba(df)[0]
            # prob_positive = float(probs[1])
            # pred_class = 1 if prob_positive >= threshold else 0
            # pred_label = LABEL_MAP[pred_class]
            # confidence_pct = f"{prob_positive * 100:.2f}%"
            probs_raw = model.predict_proba(df)[0]  # например [P(no_fire), P(fire)]
            probs = {
                "no_fire": float(probs_raw[0]),
                "fire":    float(probs_raw[1])
            }

            # 4e) Определяем вероятность "пожара" и итоговый класс
            prob_positive = probs["fire"]  # вероятность класса "пожар"
            pred_class    = 1 if prob_positive >= threshold else 0
            pred_label    = LABEL_MAP[pred_class]
            confidence_pct = f"{prob_positive * 100:.2f}%"

            # 5) Обновляем prediction в БД
            rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
            if not rec:
                raise ValueError(f"Prediction not found for event_id={event_id}")

            rec.status = "SUCCESS"
            rec.variant = customer
            rec.score = prob_positive * 100
            rec.result = pred_label
            rec.payload = {
                "probs":          probs,           # словарь {"no_fire": x, "fire": y}
                "prob_positive":  prob_positive,   # float
                "pred_class":     pred_class,      # 0 или 1
                "pred_label":     pred_label,      # строка из LABEL_MAP
                "confidence_pct": confidence_pct   # строка вида "38.50%"
            }
            session.commit()

            return {
                "event_id": event_id
            }

        except Exception as e:
            session.rollback()
            rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
            if rec:
                rec.status = "FAILED"
                # rec.result = session.commit()
                session.commit()
            return {
                "event_id": event_id,
                "status": "FAILED",
                "error": str(e)
            }

@shared_task(
    name="worker.tasks.process_ensemble_task",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    acks_late=True
)
def process_ensemble_task(
    event_id: str,
    image_b64: str,
    latitude: float,
    longitude: float,
    date_str: Optional[str],  # либо "YYYY-MM-DD", либо None
    forecast: Optional[int],
    customer: str,
    alpha: float
) -> dict:
    """
    1) Декодирует image_b64 → PIL.Image.
    2) Получает прогноз погоды (get_daily_weather).
    3) Если «Невалидный день» → обновляет prediction.status="FAILED" и завершает.
    4) Иначе:
       a) p_cnn = вероятность пожара по CNN.
       b) (model_tabular, threshold, _) = get_model_and_threshold(customer).
       c) p_tab = вероятность пожара табличной модели.
       d) p_final = alpha * p_tab + (1 – alpha) * p_cnn.
       e) Если p_final ≤ 0.5 → категория = 0 (no_fire).
          Если p_final > 0.5 и p_tab < 0.5 → категория = 2 (anthropogenic_fire).
          Если p_final > 0.5 и p_tab ≥ 0.5 → категория = 1 (natural_fire).
    5) Обновляет Prediction: status="SUCCESS", variant="ensemble_<customer>", score=p_final, result=LABEL_MAP_E[категория].
    6) При ошибке: rollback, статус="FAILED", result=текст ошибки.
    """
    with create_session() as session:
        try:
            # 1) Декодируем изображение
            try:
                img_data = base64.b64decode(image_b64)
                image = Image.open(BytesIO(img_data)).convert("RGB")
            except Exception as img_err:
                raise ValueError(f"Failed to load image: {img_err}")

            # 2) Берём прогноз погоды
            weather_data = get_daily_weather(
                latitude=latitude,
                longitude=longitude,
                date=date_str,
                forecast=forecast
            )

            # 3) Проверяем, нет ли “Невалидный день”
            if "Невалидный день" in weather_data:
                rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
                if rec:
                    rec.status = "FAILED"
                    missing = weather_data.get("Отсутствуют признаки")
                    if missing:
                        rec.result = f"{weather_data['Невалидный день']}. Missing: {missing}"
                    else:
                        rec.result = weather_data["Невалидный день"]
                session.commit()
                return {
                    "event_id": event_id,
                    "status": "FAILED",
                    "reason": weather_data["Невалидный день"]
                }

            # 4a) Получаем p_cnn и корректно «инвертируем» для метки "no_fire"
            cnn_pred = predict_cnn(image)
            label_cnn = cnn_pred["predicted_label"]         # "wildfire" или "no_fire"
            cnn_conf_str = cnn_pred["confidence_pct"]       # например, "100.00%", "85.23%"
            conf_val = float(cnn_conf_str.replace("%", "")) / 100  # конвертируем в [0,1]

            if label_cnn == "wildfire":
                p_cnn = conf_val
            else:  # label_cnn == "no_fire"
                p_cnn = 1.0 - conf_val

            logger.info("CNN: %s (label=%s)", p_cnn, label_cnn)

            # 4b) Получаем табличную модель, её threshold и описание
            model_tabular, threshold, description = get_model_and_threshold(customer)

            # 4c) Собираем DataFrame из weather_data
            features = {
                str(feat): weather_data[str(feat)]
                for feat in model_tabular.feature_names_in_
            }
            df = pd.DataFrame([features], columns=model_tabular.feature_names_in_)

            # 4d) Получаем p_tab (вероятность класса “пожар” табличной модели)
            p_tab = model_tabular.predict_proba(df)[0][1]
            logger.info("p_tab: %s", p_tab)

            # 4e) Вычисляем p_final = alpha * p_tab + (1 – alpha) * p_cnn
            p_final = alpha * p_tab + (1.0 - alpha) * p_cnn
            logger.info("final: %s", p_final)

            # 4f) Определяем категорию
            if p_final <= 0.5:
                category = 0  # no_fire
            else:
                if p_tab < 0.5:
                    category = 2  # anthropogenic_fire
                else:
                    category = 1  # natural_fire

            # 5) Обновляем Prediction в БД
            rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
            if not rec:
                raise ValueError(f"Prediction not found for event_id={event_id}")

            rec.status = "SUCCESS"
            rec.variant = f"ensemble_cnn_{customer}"
            rec.score = float(p_final) * 100 if p_final is not None else None
            rec.result = LABEL_MAP_E[category]
            rec.payload = {
                            # Вероятность "пожара" от CNN (дробное число 0.0–1.0 и в процентах отдельно)
                            "p_cnn":           p_cnn,
                            "p_cnn_pct":       f"{p_cnn * 100:.2f}%", 

                            # Вероятность "пожара" от табличной модели (дробное и процент)
                            "p_tab":           p_tab,
                            "p_tab_pct":       f"{p_tab * 100:.2f}%", 

                            # Итоговая объединённая вероятность (дробная и процент)
                            "p_final":         p_final,
                            "p_final_pct":     f"{p_final * 100:.2f}%", 

                            # Параметры алгоритма
                            "alpha":           alpha,
                            "threshold_tau":   0.5,           # мы жёстко используем τ = 0.5
                            "tab_threshold":   threshold,     # если нужно, можно отобразить порог табличной модели
                            "cnn_label":       label_cnn,     # какая метка вернулась от CNN
                            "cnn_confidence":  cnn_conf_str,   # оригинальная строка, например "85.23%"

                            # Итоговая категория и её текстовое обозначение
                            "category":        category,
                            "category_label":  LABEL_MAP_E[category]
                        }

            session.commit()

            return {
                "event_id": event_id,
                "status": "SUCCESS"
            }

        except Exception as e:
            session.rollback()
            rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
            if rec:
                rec.status = "FAILED"
                rec.result = str(e)[:255]
                session.commit()
            else:
                session.commit()
            return {
                "event_id": event_id,
                "status": "FAILED",
                "error": str(e)
            }


def process_cnn_data(image_input: str, event_id: str, session, is_base64: bool = True) -> dict:
    try:
        if is_base64:
            image_data = base64.b64decode(image_input)
            image = Image.open(BytesIO(image_data)).convert("RGB")
        else:
            image = Image.open(image_input).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to load image: {e}"}

    try:
        rec = run_cnn_prediction(image, event_id, session)
        session.commit()
        return {"predicted_label": rec.result, "confidence_pct": rec.score}
    except Exception as e:
        session.rollback()
        return {"error": str(e)}

        # rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
        # if not rec:
        #     logger.error(f"No Prediction found for event_id={event_id}")
        #     return {"error": "Prediction record not found"}

        # logger.info("Before update: %s", rec.to_dict())

        # rec.status = 'SUCCESS'
        # rec.variant = 'CNN'
        # rec.score = float(str(result.get('confidence_pct')).rstrip('%'))
        # rec.result = result.get('predicted_label')

        # session.commit()

        # logger.info("After update: %s", rec.to_dict())

        # return {"predicted_label": rec.result, "confidence_pct": rec.score}


# @shared_task
# def process_cnn_data_task(image_bytes_b64: str, event_id: str):
#     image_bytes = base64.b64decode(image_bytes_b64)
#     image = Image.open(BytesIO(image_bytes)).convert("RGB")

#     result = predict_cnn(image)

#     print(f"[CNN TASK] Event ID: {event_id} — Result: {result}")

#     return result

#Старая версия
# @shared_task
# def process_cnn_data_task(image_input: str, event_id: str, is_base64: bool = True) -> dict:
#     session = SessionLocal()
#     try:
#         if is_base64:
#             image_data = base64.b64decode(image_input)
#             image = Image.open(BytesIO(image_data)).convert("RGB")
#         else:
#             image = Image.open(image_input).convert("RGB")
#     except Exception as e:
#         return {"error": f"Failed to load image: {e}"}
    
#     result = predict_cnn(image)

#     rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
#     if rec:
#         logger.info("Before update: %s", rec.to_dict())

#         rec.status = 'SUCCESS'
#         rec.variant = result.get('predicted_label')
#         rec.score = float(str(result.get('confidence_pct')).rstrip('%'))
#         rec.result = result.get('predicted_label')  # или str(result), если нужно всё

#         session.add(rec)  # <= на всякий случай
#         session.commit()

#         logger.info("After update: %s", rec.to_dict())

#     return result.get('predicted_label')