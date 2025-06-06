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
st.title(f"Сервис определения лесного пожара по метеоданным (**{model}**)")

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

with st.form("fire_predict_form", clear_on_submit=False):
    st.subheader("Введите данные для прогноза пожара")
    latitude = st.number_input(
        "Широта (latitude)",
        value=st.session_state.get("latitude", 55.0),
        format="%.6f",
        key="latitude_widget"
    )
    longitude = st.number_input(
        "Долгота (longitude)",
        value=st.session_state.get("longitude", 37.0),
        format="%.6f",
        key="longitude_widget"
    )
    date_input = st.date_input(
        "Дата прогноза",
        value=st.session_state.get("date_input", date.today()),
        key="date_input_widget"
    )
    forecast = st.number_input(
        "Дни вперёд или назад (forecast)",
        min_value=-16,
        max_value=16,
        value=st.session_state.get("forecast", 0),
        key="forecast_widget"
    )
    submitted = st.form_submit_button("Отправить запрос на прогноз")

if submitted:
    # Сохраняем в session_state, чтобы не терять при перерисовке
    st.session_state["latitude"] = st.session_state["latitude_widget"]
    st.session_state["longitude"] = st.session_state["longitude_widget"]
    st.session_state["date_input"] = st.session_state["date_input_widget"]
    st.session_state["forecast"] = st.session_state["forecast_widget"]

    payload = {
        "user_id": user_id,
        "latitude": st.session_state["latitude"],
        "longitude": st.session_state["longitude"],
        "date": st.session_state["date_input"].strftime("%Y-%m-%d"),
        "forecast": st.session_state["forecast"],
        "customer": "cb_xgb"
    }

    try:
        resp = requests.post(
            "http://app:8080/weather/predict",
            json=payload,
            cookies={COOKIE_NAME: access_token},
            timeout=10
        )
        if resp.status_code == 200:
            event_id = resp.json()
            st.success(f"Прогноз поставлен в очередь, event_id: {event_id}")
            prediction_url = f"http://app:8080/predictions/{event_id}"
            placeholder = st.empty()

            with st.spinner("Ожидаем завершения прогноза..."):
                for _ in range(10):
                    pred_resp = requests.get(
                        prediction_url,
                        cookies={COOKIE_NAME: access_token},
                        timeout=5
                    )
                    if pred_resp.status_code == 200:
                        prediction = pred_resp.json()
                        if prediction.get("status") == "SUCCESS":
                            result = prediction.get("result", "—")
                            payload_data = prediction.get("payload", {})
                            probs = payload_data.get("probs", {})

                            # вытаскиваем вероятность предсказанного класса
                            prob = probs.get(result, 0.0)
                            score = f"{round(prob * 100, 2)}%"

                            # Сохраняем результат прогноза пожара
                            st.session_state["fire_result"] = result
                            st.session_state["fire_score"] = f"{score}"

                            # Основные результаты
                            main_table = pd.DataFrame({
                                "Параметр": ["Результат", "Вероятность"],
                                "Значение": [result, f"{score}"]
                            })
                            st.session_state["main_table"] = main_table
                            st.session_state["payload_data"] = payload_data

                            placeholder.success("Прогноз готов!")
                            placeholder.table(main_table)

                            # Дополнительные данные
                            if payload_data:
                                # Словарь перевода ключей payload_data
                                key_map = {
                                    "probs":          "Вероятности по классам",
                                    "prob_positive":  "Итоговая вероятность пожара",
                                    "pred_class":     "Класс предсказания",
                                    "pred_label":     "Метка предсказания",
                                    "confidence_pct": "Уверенность"
                                }

                                rows = []
                                for key, val in payload_data.items():
                                    ru_key = key_map.get(key, key)  # замена на русский или оставляем оригинал, если нет перевода
                                    # Если ключ = "probs", то val — словарь {"no_fire": x, "fire": y}. Превратим в строку:
                                    if key == "probs" and isinstance(val, dict):
                                        # берём именно те ключи, которые вы положили в rec.payload["probs"]
                                        nowildfire_val = val.get("nowildfire", 0.0)
                                        wildfire_val    = val.get("wildfire", 0.0)
                                        val_str = f"nowildfire: {nowildfire_val:.4f}, wildfire: {wildfire_val:.4f}"
                                    else:
                                        val_str = str(val)
                                    rows.append({"Параметр": ru_key, "Значение": val_str})

                                df_payload = pd.DataFrame(rows)
                                st.table(df_payload)

                            break
                            #     st.subheader("Дополнительные данные:")
                            #     df_payload = pd.DataFrame(
                            #             [(k, str(v)) for k, v in payload_data.items()],
                            #             columns=["Параметр", "Значение"]
                            #         )
                            #     st.table(df_payload)
                            # break
                    time.sleep(1)
        elif resp.status_code == 404:
            st.error(f"Ошибка: {resp.json().get('detail', 'Не найдено')}")
        else:
            st.error(f"Ошибка сервера: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Ошибка соединения: {e}")

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

# === Кнопка возврата в личный кабинет ===
st.markdown("---")
if st.button("⬅ Назад в личный кабинет"):
    st.switch_page("pages/cab.py")


# ВЕРСИЯ БЕЗ СОХРАНЕНИЯ ПРОГНОЗА ДЛЯ ОТОБРАЖЕНИЯ ПРИ ЗАПРОСЕ ПОЧАСОВОГО
# import streamlit as st
# import requests
# from extra_streamlit_components import CookieManager
# import settings
# from datetime import date
# import time
# import pandas as pd

# COOKIE_NAME = settings.COOKIE_NAME
# cookie_manager = CookieManager()


# access_token = cookie_manager.get(COOKIE_NAME)

# if not access_token:
#     st.error("Вы не авторизованы. Пожалуйста, войдите.")
#     if st.button("⬅ Назад к авторизации"):
#                 st.switch_page("Home.py")
#     st.stop()

# #для перевода градусов в направление ветра ===
# def get_wind_direction_info(deg: float) -> tuple[str, str]:
#     """
#     Возвращает кортеж (откуда дует ветер, куда дует ветер) в словесном виде.
#     Азимут (deg) означает, откуда дует ветер (градусы от 0 до 360).
#     """
#     def deg_to_name(d: float) -> str:
#         directions = [
#             "Север", "Северо-восток", "Восток", "Юго-восток",
#             "Юг", "Юго-запад", "Западный", "Северо-запад"
#         ]
#         ix = int((d + 22.5) % 360 // 45)
#         return directions[ix]

#     from_deg = deg % 360
#     to_deg = (deg + 180) % 360
#     return deg_to_name(from_deg), deg_to_name(to_deg)

# model = st.session_state.get("selected_model", "Не выбрана")

# st.title(f"Сервис определения лесного пожара по метеоданным (**{model}**)")

# user_id = None

# try:
#     response = requests.get(
#         "http://app:8080/auth",
#         cookies={COOKIE_NAME: access_token},
#         timeout=5
#     )
#     if response.status_code == 200:
#         user_id = response.json().get("user_id")
#     else:
#         st.error("Ошибка при получении ID пользователя")
#         st.stop()
# except Exception as e:
#     st.error(f"Ошибка соединения: {e}")
#     st.stop()

# with st.form("fire_predict_form"):
#     st.subheader("Введите данные для прогноза пожара")
#     latitude = st.number_input("Широта (latitude)", value=55.0, format="%.6f")
#     longitude = st.number_input("Долгота (longitude)", value=37.0, format="%.6f")
#     date_input = st.date_input("Дата прогноза", value=date.today())
#     forecast = st.number_input("Дни вперёд или назад (forecast)", max_value=16, value=0)

#     submitted = st.form_submit_button("Отправить запрос на прогноз")

# if submitted:
    
#     # Формируем тело запроса
#     payload = {
#         "user_id": user_id,
#         "latitude": latitude,
#         "longitude": longitude,
#         "date": date_input.strftime("%Y-%m-%d"),
#         "forecast": forecast,
#         "customer": "cb_xgb"
#     }

#     try:
#         resp = requests.post(
#             "http://app:8080/weather/predict",
#             json=payload,
#             cookies={COOKIE_NAME: access_token},
#             timeout=10
#         )
#         if resp.status_code == 200:
#             event_id = resp.json()
#             st.success(f"Прогноз поставлен в очередь, event_id: {event_id}")
#             prediction_url = f"http://app:8080/predictions/{event_id}"
#             placeholder = st.empty()
#             with st.spinner("Ожидаем завершения прогноза..."):
#                 for _ in range(20):
#                     pred_resp = requests.get(prediction_url, cookies={COOKIE_NAME: access_token}, timeout=5)
#                     if pred_resp.status_code == 200:
#                         prediction = pred_resp.json()
#                         # st.json(prediction)
#                         if prediction.get("status") == "SUCCESS":
#                             # st.success("Прогноз готов!")
#                             # st.write(f"Результат: {prediction.get('result')}")
#                             # st.write(f"Вероятность: {prediction.get('score')}")
#                             # st.json(prediction.get("payload"))
#                             result = prediction.get("result", "—")
#                             score = str(round(prediction.get("score", 0), 2))+'%'
#                             payload_data = prediction.get("payload", {})

#                         # Основные результаты
#                             main_table = pd.DataFrame({
#                                 "Параметр": ["Результат", "Вероятность"],
#                                 "Значение": [result, score]
#                             })
#                             placeholder.success("Прогноз готов!")
#                             st.table(main_table)

#                         # Дополнительные данные
#                             if payload_data:
#                                 st.subheader("Дополнительные данные:")
#                                 df_payload = pd.DataFrame(payload_data.items(), columns=["Параметр", "Значение"])
#                                 st.table(df_payload)
#                             break
#                     time.sleep(1)
#         elif resp.status_code == 404:
#             st.error(f"Ошибка: {resp.json().get('detail', 'Не найдено')}")
#         else:
#             st.error(f"Ошибка сервера: {resp.status_code} - {resp.text}")
#     except Exception as e:
#         st.error(f"Ошибка соединения: {e}")

# st.markdown("---")
# with st.expander("Почасовой прогноз"):
#     hours_ahead = st.number_input("Через сколько часов?", min_value=0, max_value=384, value=1)
#     if st.button("Запросить почасовой прогноз"):
#         forecast_url = "http://app:8080/weather/forecast-hourly/"
#         params = {"lat": latitude, "lon": longitude, "hours_ahead": hours_ahead}

#         MAX_ATTEMPTS = 10
#         WAIT_SECONDS = 2
#         success = False

#         for attempt in range(MAX_ATTEMPTS):
#             st.info(f"Попытка {attempt + 1}: получаем данные...")
#             try:
#                 response = requests.get(
#                     forecast_url,
#                     params=params,
#                     cookies={COOKIE_NAME: access_token},
#                     timeout=10
#                 )
#                 if response.status_code == 200:
#                     data = response.json()
#                     if data:
#                         st.success("Прогноз получен:")
#                         if isinstance(data, dict):
#                             data = [data]
                        
#                         df = pd.DataFrame(data)
#                         df.rename(columns={
#                             "time": "Время (UTC)",
#                             "temperature_2m": "Температура (высота 2 м, °C)",
#                             "temperature_10m": "Температура (высота 10 м, °C)",
#                             "wind_speed_10m": "Скорость ветра (высота 10 м, м/с)",
#                             "wind_direction_10m": "Азимут ветра (высота 10 м, °)",
#                             "wind_gusts_10m": "Порывы ветра (высота 10 м, м/с)"
#                         }, inplace=True)

#                         if "Азимут ветра (высота 10 м, °)" in df.columns:
#                             df["Откуда дует ветер"] = df["Азимут ветра (высота 10 м, °)"].apply(
#                                 lambda x: get_wind_direction_info(x)[0]
#                             )
#                             df["Куда дует ветер"] = df["Азимут ветра (высота 10 м, °)"].apply(
#                                 lambda x: get_wind_direction_info(x)[1]
#                             )
#                         st.dataframe(df.round(2), use_container_width=True)
#                         success = True
#                         break
#                     else:
#                         st.warning(f"Попытка {attempt + 1}: данные ещё не готовы. Ждём {WAIT_SECONDS}с...")
#                 else:
#                     st.error(f"Ошибка: {response.status_code} - {response.text}")
#                     break
#             except Exception as e:
#                 st.error(f"Ошибка запроса: {e}")
#             time.sleep(WAIT_SECONDS)

#         if not success:
#             st.error("Не удалось получить прогноз. Попробуйте позже.")



# st.markdown("---")

# if st.button("⬅ Назад в личный кабинет"):
#     st.switch_page("pages/cab.py")