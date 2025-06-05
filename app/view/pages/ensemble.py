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
    forecast = st.number_input("Смещение (дней от сегодня)", min_value=0, max_value=16, value=0)
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
                st.success(f"Задача принята! event_id: {response.json()['event_id']}")
            else:
                st.error(f"Ошибка: {response.status_code} — {response.text}")
        except Exception as e:
            st.error(f"Ошибка при подключении: {e}")
elif submit:
    st.warning("Пожалуйста, загрузите изображение.")


st.markdown("---")

if st.button("⬅ Назад в личный кабинет"):
    st.switch_page("pages/cab.py")