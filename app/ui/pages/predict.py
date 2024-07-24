import streamlit as st
import requests

import settings as settings


settings.set_wide()
settings.create_navbar()
cookie_manager = settings.get_manager()
access_token = cookie_manager.get("access_token")
settings.token_check(access_token)

st.title("НОВЫЙ ЗАПРОС")

pregnancies = st.number_input('Кол-во беременностей', min_value=0.0, max_value=20.0, value=5.0, step=1.0)
glucose = st.number_input('Глюкоза', min_value=0.0, max_value=250.0, value=150.0, step=1.0)
blood_pressure = st.number_input('Артериальное давление', min_value=0.0, max_value=125.0, value=20.0, step=1.0)
skin_thickness = st.number_input('Толщина кожи', min_value=0.0, max_value=100.0, value=60.0, step=1.0)
insulin = st.number_input('Инсулин', min_value=0.0, max_value=900.0, value=400.0, step=1.0)
bmi = st.number_input('Индекс массы тела (ИТМ)', min_value=0.0, max_value=70.0, value=15.0, step=1.0)
pedigree = st.number_input('Функция определения родословной диабета', min_value=0.03, max_value=3.0, value=1.0, step=0.01)
age = st.number_input('Возраст', min_value=1.0, max_value=100.0, value=35.0, step=1.0)


if st.button('ОТПРАВИТЬ ЗАПРОС (20 coins)'):
    # Form the request payload
    payload = {
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "Blood_Pressure": blood_pressure,
        "Skin_Thickness": skin_thickness,
        "Insulin": insulin,
        "BMI": bmi,
        "Diabetes_Pedigree_Function": pedigree,
        "Age": age
    }

    # Send the POST request to your FastAPI app
    response = requests.post("http://app:8080/predict/" + str(access_token), json=payload)
    if response.status_code == 200:
        prediction = response.json()['predicted_status']
        if prediction == '0':
            st.success('Признаков диабета не выявлено')
        else:
            st.error('Возможно у вас диабет')   
    else:
        if response.status_code in [409]:
            error_desc = response.json()["detail"]
            st.error("""Ваш баланс меньше стоимости запроса""")
        else:
            st.error('Error in prediction')

if st.button("Выйти из аккаунта", use_container_width=True):
    cookie_manager.delete("access_token")
