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
                                                 , "Список транзакций"])

if page == "Список пользователей":
    st.title("Список пользователей")

    response = requests.get('http://app:8080/user/all_users')
    response_df_detail = pd.DataFrame(response.json())

    if len(response_df_detail) == 0:
        st.success('Пользователи отсутствуют')
    else:
        response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
        st.dataframe(response_df_detail)

if page == "Список запросов":
    st.title("Список запросов")

    response = requests.get('http://app:8080/user/all_his')
    response_df_detail = pd.DataFrame(response.json())

    if len(response_df_detail) == 0:
        st.success('Запросы отсутствуют')
    else:
        response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
        st.dataframe(response_df_detail)

if page == "Список транзакций":
    st.title("Список транзакций")

    response = requests.get('http://app:8080/user/all_tr')
    response_df_detail = pd.DataFrame(response.json())

    if len(response_df_detail) == 0:
        st.success('Транзакции отсутствуют')
    else:
        response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
        st.dataframe(response_df_detail)