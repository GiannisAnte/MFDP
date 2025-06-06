import streamlit as st
import requests
from extra_streamlit_components import CookieManager
import settings
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

model = st.session_state.get("selected_model", "Не выбрана")

st.title(f"Сервис определения лесного пожара по спутниковым снимкам (**{model}**)")

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

uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Загруженное изображение", use_column_width=True)

    if st.button("Отправить на предсказание"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        try:
            response = requests.post(
                f"http://app:8080/predict/cnn/",
                params={"user_id": user_id},
                files=files
            )
            if response.status_code == 200:
                event_id = response.json().get("event_id")
                st.success(f"Изображение отправлено. ID задачи: {event_id}")
                prediction_url = f"http://app:8080/predictions/{event_id}"
                placeholder = st.empty()
                with st.spinner("Ожидаем завершения прогноза..."):
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
                                score = str(round(prediction.get("score", 0), 2)) + '%'
                                payload_data = prediction.get("payload", {})

                                # st.session_state["fire_result"] = result
                                # st.session_state["fire_score"] = f"{score} %"

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
                                    # df_payload = pd.DataFrame(payload_data.items(), columns=["Параметр", "Значение"])
                                    df_payload = pd.DataFrame(
                                        [(k, str(v)) for k, v in payload_data.items()],
                                        columns=["Параметр", "Значение"]
                                    )
                                    st.table(df_payload)
                                break
                        time.sleep(1)
            else:
                st.error(f"Ошибка: {response.status_code} — {response.text}")
        except Exception as e:
            st.error(f"Ошибка при отправке запроса: {e}")

st.markdown("---")

if st.button("⬅ Назад в личный кабинет"):
    st.switch_page("pages/cab.py")

