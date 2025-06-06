import streamlit as st
import requests
from extra_streamlit_components import CookieManager
import settings
from datetime import date
import time
import pandas as pd

COOKIE_NAME = settings.COOKIE_NAME
cookie_manager = CookieManager()


access_token = cookie_manager.get(COOKIE_NAME)

if not access_token:
    st.error("Вы не авторизованы. Пожалуйста, войдите.")
    if st.button("⬅ Назад к авторизации"):
                st.switch_page("Home.py")
    st.stop()

# для перевода градусов в направление ветра:
def get_wind_direction_info(deg: float) -> tuple[str, str]:
    """
    Возвращает кортеж (откуда дует ветер, куда дует ветер) в словесном виде.
    Азимут (deg) означает, откуда дует ветер (градусы от 0 до 360).
    """
    def deg_to_name(d: float) -> str:
        directions = [
            "Север", "Северо-восток", "Восток", "Юго-восток",
            "Юг", "Юго-запад", "Запад", "Северо-запад"
        ]
        ix = int((d + 22.5) % 360 // 45)
        return directions[ix]

    from_deg = deg % 360
    to_deg = (deg + 180) % 360
    return deg_to_name(from_deg), deg_to_name(to_deg)

model = st.session_state.get("selected_model", "Не выбрана")

st.title(f"Сервис определения лесного пожара на основе ансамбля CNN и метеомодели (изображение + погода)")

user_id = None

try:
    response = requests.get(
        "http://app:8080/auth",
        cookies={COOKIE_NAME: access_token},
        timeout=5
    )
    if response.status_code == 200:
        user_id = response.json().get("user_id")
    else:
        st.error("Ошибка при получении ID пользователя")
        st.stop()
except Exception as e:
    st.error(f"Ошибка соединения: {e}")
    st.stop()

model_options = {
    "CatBoost + XGBoost": "cb_xgb",
    "CatBoost + RF": "cb_rf"
}

selected_label = st.selectbox("Выберите метеомодель:", list(model_options.keys()))

with st.form("ensemble_form"):
    st.subheader("Введите данные")
    latitude = st.number_input("Широта", value=55.0, format="%.6f")
    longitude = st.number_input("Долгота", value=37.0, format="%.6f")
    date_input = st.date_input("Дата прогноза", value=date.today())
    forecast = st.number_input("Смещение (дней от сегодня)", min_value=-16, max_value=16, value=0)
    alpha = st.slider("Вес табличной модели (α)", 0.0, 1.0, 0.5, step=0.05)
    customer = model_options[selected_label]
    uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])

    submit = st.form_submit_button("Отправить на предсказание")

if submit and uploaded_file:
    st.image(uploaded_file, caption="Загруженное изображение", use_column_width=True)

    url = "http://app:8080/predict/ensemble/"  # замените на ваш URL
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }
    params = {
        "user_id": user_id,
        "lat": latitude,
        "lon": longitude,
        "target_date": date_input.isoformat(),
        "forecast": forecast,
        "customer": customer,
        "alpha": alpha,
    }

    # Отправка запроса
    with st.spinner("Отправка на сервер..."):
        try:
            response = requests.post(url, params=params, files=files)
            if response.status_code == 200:
                event_id = response.json().get("event_id")
                st.success(f"Задача принята! event_id: {response.json()['event_id']}")
                prediction_url = f"http://app:8080/predictions/{event_id}"
                placeholder = st.empty()
                with st.spinner("Ожидаем завершения прогноза..."):
                    time.sleep(2)
                    for _ in range(20):
                        pred_resp = requests.get(prediction_url, cookies={COOKIE_NAME: access_token}, timeout=5)
                        if pred_resp.status_code == 200:
                            prediction = pred_resp.json()
                            # st.json(prediction)
                            if prediction.get("status") == "SUCCESS":
                                # st.success("Прогноз готов!")
                                # st.write(f"Результат: {prediction.get('result')}")
                                # st.write(f"Вероятность: {prediction.get('score')}")
                                # st.json(prediction.get("payload"))
                                result = prediction.get("result", "—")
                                # score = str(round(prediction.get("score", 0), 2)) + '%'
                                # result = "nowildfire" или "wildfire"
                                
                                payload_data = prediction.get("payload", {})
                                probs = payload_data.get("probs", {})  # например {'nowildfire': 0.945, 'wildfire': 0.055}
                                prob_of_result = probs.get(result, 0.0)               # float: 0.945 или 0.055
                                score = f"{payload_data.get('p_final', 0.0) * 100:.2f}%"

                                st.session_state["fire_result"] = result
                                st.session_state["fire_score"] = f"{score}"

                            # Основные результаты
                                main_table = pd.DataFrame({
                                    "Параметр": ["Результат", "Вероятность"],
                                    "Значение": [result, score]
                                })
                                placeholder.success("Прогноз готов!")
                                st.table(main_table)

                            # Дополнительные данные
                                if payload_data:
                                    st.subheader("Дополнительные данные:")
                                    key_map = {
                                        "p_cnn":           "Вероятность (CNN, число)",
                                        "p_cnn_pct":       "Вероятность (CNN, %)",
                                        "cnn_label":       "Метка CNN",
                                        "p_tab":           "Вероятность (погода, число)",
                                        "tab_label":       "Метка табличной модели",
                                        "p_tab_pct":       "Вероятность (погода, %)",
                                        "p_final":         "Итоговая вероятность (число)",
                                        "p_final_pct":     "Итоговая вероятность (процент)",
                                        "alpha":           "Вес α (табличная модель)",
                                        "category":        "Категория (число)",
                                        "category_label":  "Категория (текст)"
                                    }

                                    rows = []
                                    for key, val in payload_data.items():
                                        ru_key = key_map.get(key, key)  # если нет в key_map, оставляем оригинал

                                        # Приведём значение к строке. Если это float, отформатируем двумя знаками после запятой.
                                        if isinstance(val, float):
                                            # Для долей (например, 0.476) выводим с 3 знаками, если надо
                                            val_str = f"{val:.3f}"
                                        else:
                                            val_str = str(val)

                                        rows.append({"Параметр": ru_key, "Значение": val_str})

                                    df_payload = pd.DataFrame(rows)
                                    st.table(df_payload)
                                break
                        time.sleep(1)
            else:
                st.error(f"Ошибка: {response.status_code} — {response.text}")
        except Exception as e:
            st.error(f"Ошибка при подключении: {e}")
elif submit:
    st.warning("Пожалуйста, загрузите изображение.")

# === Почасовой прогноз ===
st.markdown("---")
with st.expander("Почасовой прогноз"):
    lat_for_hourly = st.session_state.get("latitude", 55.0)
    lon_for_hourly = st.session_state.get("longitude", 37.0)

    hours_ahead = st.number_input(
        "Через сколько часов?",
        min_value=0,
        max_value=384,
        value=st.session_state.get("hours_ahead", 1),
        key="hours_ahead_widget"
    )
    if st.button("Запросить почасовой прогноз"):
        st.session_state["hours_ahead"] = st.session_state["hours_ahead_widget"]

        # Формируем заголовок, используя latitude, longitude, и свежий прогноз пожара
        fire_res = st.session_state.get("fire_result", "—")
        fire_s = st.session_state.get("fire_score", "—")
        header_text = (
            f"Почасовой прогноз для {lat_for_hourly}, {lon_for_hourly}; "
            f"прогноз пожара: {fire_res}, {fire_s}"
        )
        placeholder_header = st.empty()
        placeholder_header.subheader(header_text)

        forecast_url = "http://app:8080/weather/forecast-hourly/"
        params = {
            "lat": lat_for_hourly,
            "lon": lon_for_hourly,
            "hours_ahead": st.session_state["hours_ahead"]
        }

        placeholder_hourly = st.empty()
        MAX_ATTEMPTS = 10
        WAIT_SECONDS = 2
        success = False

        for attempt in range(MAX_ATTEMPTS):
            placeholder_hourly.info(f"Попытка {attempt + 1}: получаем данные...")
            try:
                response = requests.get(
                    forecast_url,
                    params=params,
                    cookies={COOKIE_NAME: access_token},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        placeholder_hourly.success("Почасовой прогноз получен:")
                        if isinstance(data, dict):
                            data = [data]
                        df = pd.DataFrame(data)

                        # Переименовываем столбцы на русский
                        df.rename(columns={
                            "time": "Время (UTC)",
                            "temperature_2m": "Температура (высота 2 м, °C)",
                            "temperature_10m": "Температура (высота 10 м, °C)",
                            "wind_speed_10m": "Скорость ветра (высота 10 м, м/с)",
                            "wind_direction_10m": "Азимут ветра (высота 10 м, °)",
                            "wind_gusts_10m": "Порывы ветра (высота 10 м, м/с)"
                        }, inplace=True)

                        # Добавляем столбцы "Откуда дует ветер" и "Куда дует ветер"
                        if "Азимут ветра (высота 10 м, °)" in df.columns:
                            df["Откуда дует ветер"] = df["Азимут ветра (высота 10 м, °)"].apply(
                                lambda x: get_wind_direction_info(x)[0]
                            )
                            df["Куда дует ветер"] = df["Азимут ветра (высота 10 м, °)"].apply(
                                lambda x: get_wind_direction_info(x)[1]
                            )

                        placeholder_hourly.dataframe(df.round(2), use_container_width=True)
                        success = True
                        break
                    else:
                        placeholder_hourly.warning(
                            f"Попытка {attempt + 1}: данные ещё не готовы. Ждём {WAIT_SECONDS}с..."
                        )
                else:
                    placeholder_hourly.error(f"Ошибка: {response.status_code} - {response.text}")
                    break

            except Exception as e:
                placeholder_hourly.error(f"Ошибка запроса: {e}")
                break

            time.sleep(WAIT_SECONDS)

        if not success:
            placeholder_hourly.error("Не удалось получить прогноз. Попробуйте позже.")


st.markdown("---")

if st.button("⬅ Назад в личный кабинет"):
    st.switch_page("pages/cab.py")