import streamlit as st

st.set_page_config(layout="wide", page_title="Fire Service", page_icon="🔥")

import requests
from extra_streamlit_components import CookieManager
from settings import COOKIE_NAME

cookie_manager = CookieManager()

# params = st.query_params
# if params.get("page") == "cab" or params.get("page") == ["cab"]:
#     st.query_params.clear()  # важно, чтобы избежать зацикливания
#     st.rerun()
access_token = cookie_manager.get(COOKIE_NAME) or ""
# if access_token:
#     st.switch_page("cab")

if st.session_state.get("should_redirect"):
    del st.session_state["should_redirect"]
    st.switch_page("pages/cab.py")

st.title("🔥 Добро пожаловать в систему прогнозирования природных пожаров")

col1, col2 = st.columns([8, 4])

with col1:
    st.write("""
        Это интеллектуальный сервис, который помогает предсказывать риски природных пожаров за 1–5 дней 
        до их возможного возникновения. Система анализирует спутниковые и метеорологические данные, 
        оценивает вероятность возгорания в конкретных географических зонах и предупреждает 
        о потенциально опасных участках. В случае обнаружения очага пожара, система прогнозирует возможные 
             сценарии его распространения с учётом погодных условий и других факторов.
        Цель проекта — повысить эффективность мониторинга и превентивного реагирования, сократить ущерб 
        от пожаров и сохранить жизни и природу.
    """)

with col2:
    signin, signup = st.tabs(["Вход", "Регистрация"])

    # --- ВХОД ---
    with signin:
        username = st.text_input("ЛОГИН", key="username")
        password = st.text_input("ПАРОЛЬ", type="password", key="password")

        if st.button("Войти", type="primary", key="signin_button"):
            if not username or not password:
                st.warning("Пожалуйста, заполните и логин, и пароль.")
            else:
                response = requests.post(
                    'http://app:8080/user/signin',
                    params={'username': username, 'password': password}
                )
                if response.status_code in (401, 404):
                    st.error("Неверная пара логин/пароль или пользователь не найден.")
                elif response.status_code == 200:
                    token = response.json().get("access_token", "")
                    if token:
                        cookie_manager.set(COOKIE_NAME, token)
                        access_token = cookie_manager.get(COOKIE_NAME)
                        st.session_state["should_redirect"] = True
                        st.success("Вы вошли!", icon="✅")
                        st.stop()
                    else:
                        st.error("Сервер не вернул токен.")
                else:
                    st.error(f"Ошибка сервера: {response.status_code}")

    # --- РЕГИСТРАЦИЯ ---
    with signup:
        new_username = st.text_input("Имя пользователя")
        email = st.text_input("E-mail")
        new_password = st.text_input("Пароль", type="password")

        if st.button("Зарегистрироваться", type="primary", key="sign_up"):
            response = requests.post('http://app:8080/user/signup',
                                     params={'username': new_username,
                                             'email': email,
                                             'password': new_password})

            if response.status_code == 422:
                st.error("Неверно задан email")
            elif response.status_code == 200:
                st.success('Пользователь зарегистрирован успешно', icon="✅")
            else:
                st.error(response.json().get('detail', 'Неизвестная ошибка'), icon="⛔️")





# import streamlit as st

# st.set_page_config(layout="wide", page_title="Fire Service", page_icon="🔥")

# import requests
# import settings


# settings.create_navbar()
# cookie_manager = settings.get_manager()
# access_token = cookie_manager.get("access_token")

# st.title("🔥 Добро пожаловать в систему прогнозирования природных пожаров")

# col1, col2 = st.columns([6, 4])
# with col1:
#     st.write("""
#         Это интеллектуальный сервис, который помогает предсказывать риски природных пожаров за 1–5 дней 
#         до их возможного возникновения. Система анализирует спутниковые и метеорологические данные, 
#         оценивает вероятность возгорания в конкретных географических зонах и предупреждает 
#         о потенциально опасных участках. В случае обнаружения очага пожара, система прогнозирует возможные 
#              сценарии его распространения с учётом погодных условий и других факторов.
#         Цель проекта — повысить эффективность мониторинга и превентивного реагирования, сократить ущерб 
#         от пожаров и сохранить жизни и природу.
#     """)

# with col2:
#     signin, signup = st.tabs(["Вход", "Регистрация"])

#     # Вкладка «Вход»
#     with signin:
#         username = st.text_input("ЛОГИН", key="username")
#         password = st.text_input("ПАРОЛЬ", type="password", key="password")
        # if st.button("Войти", type="primary", key="signin"):
        #     response = requests.post('http://app:8080/user/signin',
        #                          params={'username': username,
        #                                  'password': password})
        #     if response.status_code in [401, 404]:
        #         error_desc = response.json()["detail"]
        #         st.error("""Неверная пара логин-пароль
        #              или такой пользователь не существует""")
        #     else:
        #         token = response.json()["access_token"]
        #         cookie_manager.set('access_token', token)
        #         access_token = cookie_manager.get("access_token")
        #         st.success('Вы вошли!', icon="✅")
        #         st.switch_page("pages/cab.py")
        # # username = st.text_input("ЛОГИН", key="username")
        # # password = st.text_input("ПАРОЛЬ", type="password", key="password")

#         # if st.button("Войти", type="primary", key="signin_button"):
#         #     if not username or not password:
#         #         st.warning("Пожалуйста, заполните и логин, и пароль.")
#         #     else:
#         #         response = requests.post(
#         #             'http://app:8080/user/signin',
#         #             params={'username': username, 'password': password}
#         #         )
#         #         if response.status_code in (401, 404):
#         #             st.error("Неверная пара логин/пароль или пользователь не найден.")
#         #         elif response.status_code == 200:
#         #             token = response.json()["access_token"]
#         #             if token:
#         #                 cookie_manager.set("access_token", token)
#         #                 access_token = cookie_manager.get("access_token")
#         #                 st.success("Вы вошли!", icon="✅")
#         #                 st.switch_page("pages/cab.py")
#         #             else:
#         #                 st.error("Сервер не вернул токен.")
#         #         else:
#         #             st.error(f"Ошибка сервера: {response.status_code}")

#     # Вкладка «Регистрация»
#     with signup:
#         new_username = st.text_input("Имя пользователя", key="signup_username")
#         new_email = st.text_input("E-mail", key="signup_email")
#         new_password = st.text_input("Пароль", type="password", key="signup_password")

#         if st.button("Зарегистрироваться", type="primary", key="signup_button"):
#             if not new_username or not new_email or not new_password:
#                 st.warning("Заполните все поля для регистрации.")
#             else:
#                 response = requests.post(
#                     'http://app:8080/user/signup',
#                     params={'username': new_username, 'email': new_email, 'password': new_password}
#                 )
#                 if response.status_code == 200:
#                     st.success("Пользователь зарегистрирован успешно", icon="✅")
#                 elif response.status_code == 422:
#                     st.error("Неверно задан email.", icon="⛔️")
#                 else:
#                     detail = response.json().get("detail", "Неизвестная ошибка.")
#                     st.error(detail, icon="⛔️")
