import streamlit as st
import extra_streamlit_components as stx
import requests


def create_navbar():
    with st.sidebar:
        st.page_link('web.py', label='Главная')
        st.page_link('pages/lk.py', label='Личный кабинет')
        st.page_link('pages/h_transac.py', label='История транзакций')
        st.page_link('pages/h_task.py', label='История запросов')
        st.page_link('pages/predict.py', label='Новый запрос')


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


def set_wide():
    st.set_page_config(layout="wide")


def token_check(token):
    response = requests.get('http://app:8080/auth/' + str(token))
    if int(response.status_code) == 200:
        pass
    else:
        st.error('Вы не авторизованы, пожалуйста, пройдите процедуру авторизации')
        if st.button('Войти', use_container_width=True):
            st.switch_page("web.py")
        st.stop()
