import streamlit as st
import requests
from extra_streamlit_components import CookieManager
import settings


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
            else:
                st.error(f"Ошибка: {response.status_code} — {response.text}")
        except Exception as e:
            st.error(f"Ошибка при отправке запроса: {e}")

st.markdown("---")

if st.button("⬅ Назад в личный кабинет"):
    st.switch_page("pages/cab.py")

