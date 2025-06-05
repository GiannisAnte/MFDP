import uuid
from unittest.mock import patch
import uuid
from pathlib import Path
from services.cnn_task_sync import enqueue_cnn_task_sync
from models.fire_event import FireEvent
from models.user import User
from models.prediction import Prediction
from worker.tasks import process_cnn_data, process_cnn_data_task
from uuid import UUID
from PIL import Image
import time
import base64

def test_predict_cnn_upload(client):
    #данные
    test_user_id = str(uuid.uuid4())
    fake_image = b"fake image content"
    files = {"file": ("sample.jpg", fake_image, "image/jpeg")}

    #Мок, чтобы не запускался реальный код
    with patch("endpoints.ml.post.enqueue_cnn_task_sync") as mock_enqueue:
        mock_enqueue.return_value = str(uuid.uuid4())

        response = client.post(
            f"/predict/cnn/?user_id={test_user_id}",
            files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data #проверка в ответе есть ключ "event_id"
        assert isinstance(data["event_id"], str) #проверка - значение "event_id" в ответе совпадает
        assert files["file"][0] == "sample.jpg"#проверка, что в запросе отправляется правильное имя файла
        assert files["file"][1] == fake_image#проверка, что содержимое файла совпадает с тем, что мы передаем
        assert files["file"][2] == "image/jpeg"#проверка, что MIME-тип файла правильный (image/jpeg)


def test_enqueue_cnn_task_sync_full_with_real_image(session):
    """
    1. Создает тестового пользователя в базе данных.
    2. Загружает реальное изображение из файла `assets/sample_fire.jpg`.
    3. Создает FireEvent, связанный с пользователем, с указанием пути к изображению.
    4. Создает Prediction с начальными параметрами для данного события.
    5. Кодирует изображение в base64, так как функция обработки принимает изображение в таком формате.
    6. Запускает функцию `process_cnn_data` синхронно, передавая изображение и event_id.
    7. Проверяет, что возвращенный результат содержит ключи `predicted_label` и `confidence_pct`.
       - `predicted_label` должен быть либо "wildfire", либо "nowildfire".
       - `confidence_pct` — число от 0 до 100.
    8. Обновляет сессию и проверяет, что запись Prediction в базе обновилась результатом модели:
       - поле `result` совпадает с `predicted_label`
       - поле `score` совпадает с `confidence_pct`
    """
    #Создаем тестового пользователя
    user = User(
        id=uuid.uuid4(),
        username="realuser",
        email="realuser@example.com",
        hashed_password="realhashed"
    )
    session.add(user)
    session.commit()

    #Загружаем реальное изображение из файлов
    image_path = Path(__file__).parent / "assets" / "sample_fire.jpg"
    assert image_path.exists(), "Файл sample_fire.jpg не найден по пути"
    with image_path.open("rb") as f:
        img_bytes = f.read()

    #Создаем FireEvent для user вручную
    fire_event = FireEvent(
        id=uuid.uuid4(),
        created_by=user.id,
        source="satellite",
        payload={
            "image_path": str(image_path),
        }
        # другие обязательные поля, если есть
    )
    session.add(fire_event)
    session.commit()
    #4
    prediction = Prediction(
        id=uuid.uuid4(),
        fire_event_id=fire_event.id,
        status="PENDING",
        variant=None,
        score=0.0,
        result=None
    )
    session.add(prediction)
    session.commit()

    #Кодируем изображение в base64, т.к. таск принимает base64 строку
    img_b64 = base64.b64encode(img_bytes).decode()

    #Запускаем таск синхронно с event_id
    result = process_cnn_data(
        image_input=img_b64,
        event_id=str(fire_event.id),
        session=session,
        is_base64=True,
    )
    session.commit()
    #Проверяем, что таск вернул корректный результат
    assert "predicted_label" in result
    print(result)
    assert result["predicted_label"] in {"wildfire", "nowildfire"}
    assert "confidence_pct" in result
    assert 0.0 <= float(result["confidence_pct"]) <= 100.0#проверяем, что confidence_pct — число в диапазоне от 0 до 100

    #Проверяем, что в базе Prediction обновился
    session.expire_all()
    predictions = session.query(Prediction).filter_by(fire_event_id=fire_event.id).all()
    assert len(predictions) > 0

    pred = predictions[0]
    assert pred.result == result["predicted_label"]
    assert pred.score == result["confidence_pct"]