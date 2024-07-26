import streamlit as st
import requests
import pandas as pd
import numpy as np
import settings as settings


settings.set_wide()
settings.create_navbar()
cookie_manager = settings.get_manager()
access_token = cookie_manager.get("access_token")
# settings.token_check(access_token)
settings.admin_check(access_token)

st.title("КАБИНЕТ АДМИНИСТРАТОРА")

page = st.sidebar.selectbox("Выбрать опцию", ["Список пользователей", "Список запросов"
                                                 , "Список транзакций", "Операции с балансом"])

if page == "Список пользователей":
    st.title("Список пользователей")

    response = requests.get('http://app:8080/user/users')
    response_df_detail = pd.DataFrame(response.json())

    if len(response_df_detail) == 0:
        st.success('Пользователи отсутствуют')
    else:
        response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
        st.dataframe(response_df_detail)
    

if page == "Список запросов":
    st.title("Список запросов")

    response = requests.get('http://app:8080/user/tasks_history')
    response_df_detail = pd.DataFrame(response.json())

    if len(response_df_detail) == 0:
        st.success('Запросы отсутствуют')
    else:
        response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
        st.dataframe(response_df_detail)

if page == "Список транзакций":
    st.title("Список транзакций")

    response = requests.get('http://app:8080/user/transaction_history')
    response_df_detail = pd.DataFrame(response.json())

    if len(response_df_detail) == 0:
        st.success('Транзакции отсутствуют')
    else:
        response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
        st.dataframe(response_df_detail)

if page == "Операции с балансом":
    st.title("Операции с балансом")

    user_id = st.text_input("ID пользователя")
    operation = st.text_input("Операция")
    try:
        if operation and len(operation) > 2:
            amount = int(operation[1:])
            
            if operation.startswith("+"):
                if st.button("Подтвердить"):
                    response = requests.post('http://app:8080/user/coins/' + str(user_id),
                                            params={'amount': amount})
                    if response.status_code == 200:
                        st.write(f"Операция: Пополнение на {operation[1:]} монет для юзера с id {user_id}")
                    else:
                        st.error("Ошибка при пополнении. Проверьте данные.")
            
            elif operation.startswith("-"):
                if st.button("Подтвердить"):
                    response = requests.put('http://app:8080/user/deduct_coin/' + str(user_id),
                                            params={'amount': amount})
                    if response.status_code == 200:
                        st.write(f"Операция: Списание {operation[1:]} монет для юзера с id {user_id}")
                    else:
                        st.error("Ошибка при списании. Проверьте данные.")
            
            else:
                st.error("Неверный формат операции. Перед суммой введите + или -")
    except ValueError:
        st.error("Неверный формат операции. Проверьте правильность ввода суммы.")
    except Exception as e:
        st.error(f"Произошла ошибка: {str(e)}")