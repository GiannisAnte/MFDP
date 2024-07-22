import streamlit as st
import requests

import settings as settings


settings.set_wide()
settings.create_navbar()
cookie_manager = settings.get_manager()
access_token = cookie_manager.get("access_token")
settings.token_check(access_token)


st.title("ЛИЧНЫЙ КАБИНЕТ")
try:
    name = requests.get('http://app:8080/user/name/',
                            params={'token': access_token})
    s_name = str(name.json())
except:
    s_name = 'unlogged user'

st.header('''Добро пожаловать, ''' + s_name + '''

''')

balance = requests.get('http://app:8080/user/balance/',
                            params={'token': access_token})

st.header("Баланс: " + str(balance.json()) + " coins")

amount = st.number_input('Пополнить баланс', step=10)



if st.button("Пополнить"):
    response = requests.post('http://app:8080/user/add_coin/',
                            params={'token': access_token,
                                    'amount': amount})
    print(response.json())
    if response.json()["message"] == "Coin added to user":
        st.success('Баланс пополнен')
    else:
        st.error('Возникла ошибка. Подробности:' + response.json()['message'])

if requests.get('http://app:8080/user/name/',
                            params={'token': access_token}).json() == 'admin':
    if st.button("Админ"):    
        st.switch_page("pages/admin.py")
            
b1, b2, b3, b4 = st.columns([4, 4, 4, 4])

with b1:
    if st.button("      История транзакций      "):        
        st.switch_page("pages/h_transac.py")
with b2:
    if st.button("      История запросов        "):        
        st.switch_page("pages/h_task.py")
with b3:
    if st.button("      Новый запрос        "):        
        st.switch_page("pages/predict.py")
with b4:
    if st.button("      Последний запрос        "):        
        st.switch_page("pages/predict.py")

if st.button("Выйти из аккаунта", use_container_width=True):
    cookie_manager.delete("access_token")
