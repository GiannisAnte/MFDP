import streamlit as st
import requests

import settings as settings

st.set_page_config(layout="wide")


settings.create_navbar()
cookie_manager = settings.get_manager()
access_token = cookie_manager.get("access_token")


st.title('''Мониторинг диабета 
         
         
         
         
        
         
         ''')
# Заголовок и описание
col1, col2 = st.columns([6, 4])

with col1:
    st.write("""
    Диабет - это не просто повышенный уровень сахара в крови. 
       - Это комплексное заболевание, которое может повлиять 
         на различные органы и системы организма.
       - Это проблема мирового масштаба: По данным Всемирной 
         организации здравоохранения, около 422 миллионов человек 
         во всем мире страдают от диабета.
       - Диабет может быть наследственным: если у вас есть родственники 
         с диабетом, вы более склонны к развитию этого заболевания.  
    """)
    st.write("""
             




    При своевременной диагностике и правильном лечении диабета 
        можно жить полноценной жизнью. Это приложение поможет вам оценить 
        риск заболевания диабетом по небольшому числу параметров, которые 
        вы можете измерить даже из дома.
    """)

# Формы
with col2:
    signin, signup = st.tabs(["Вход", "Регистрация"])

    with signin:
        username = st.text_input("ЛОГИН", key="username")
        password = st.text_input("ПАРОЛЬ", type="password", key="password")
        if st.button("Войти", type="primary", key="signin"):
            response = requests.post('http://app:8080/user/signin',
                                 params={'username': username,
                                         'password': password})
            if response.status_code in [401, 404]:
                error_desc = response.json()["detail"]
                st.error("""Неверная пара логин-пароль
                     или такой пользователь не существует""")
            else:
                token = response.json()["access_token"]
                cookie_manager.set('access_token', token)
                st.success('Вы вошли!', icon="✅")

        if st.button("Перейти в личный кабинет"):
            if access_token != '':        
                st.switch_page("pages/lk.py")

    with signup:
        username = st.text_input("Имя пользователя")
        email = st.text_input("E-mail")
        password = st.text_input("Пароль", type="password")

        if st.button("Зарегистрироваться", type="primary", key="sign_up"):
            response = requests.post('http://app:8080/user/signup',
                                 params={'username': username,
                                         'email': email,
                                         'password': password})
            if response.status_code == 200:
                message = response.json()
                st.success('Пользователь зарегистрирован успешно', icon="✅")
            else:
                message = response.json()
                st.error(message['detail'], icon="⛔️")

