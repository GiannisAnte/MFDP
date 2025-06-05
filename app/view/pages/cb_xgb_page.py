import streamlit as st
import requests
from extra_streamlit_components import CookieManager
import settings
from datetime import date

COOKIE_NAME = settings.COOKIE_NAME
cookie_manager = CookieManager()


access_token = cookie_manager.get(COOKIE_NAME)

if not access_token:
    st.error("Вы не авторизованы. Пожалуйста, войдите.")
    if st.button("⬅ Назад к авторизации"):
                st.switch_page("Home.py")
    st.stop()

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

with st.form("fire_predict_form"):
    st.subheader("Введите данные для прогноза пожара")
    latitude = st.number_input("Широта (latitude)", value=55.0, format="%.6f")
    longitude = st.number_input("Долгота (longitude)", value=37.0, format="%.6f")
    date_input = st.date_input("Дата прогноза", value=date.today())
    forecast = st.number_input("Дни вперёд или назад (forecast)", min_value=0, max_value=16, value=0)

    submitted = st.form_submit_button("Отправить запрос на прогноз")

if submitted:
    # Формируем тело запроса
    payload = {
        "user_id": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "date": date_input.strftime("%Y-%m-%d"),
        "forecast": forecast,
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
        elif resp.status_code == 404:
            st.error(f"Ошибка: {resp.json().get('detail', 'Не найдено')}")
        else:
            st.error(f"Ошибка сервера: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Ошибка соединения: {e}")



st.markdown("---")

if st.button("⬅ Назад в личный кабинет"):
    st.switch_page("pages/cab.py")