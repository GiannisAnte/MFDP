import streamlit as st
import requests
import settings as settings
import pandas as pd
import json
import numpy as np


settings.set_wide()
settings.create_navbar()
cookie_manager = settings.get_manager()
access_token = cookie_manager.get("access_token")
settings.token_check(access_token)

st.title("История транзакций")

response = requests.get('http://app:8080/user/transactions/' + str(access_token))
response_df_detail = pd.DataFrame(response.json())

if len(response_df_detail) == 0:
    st.success('Транзакции отсутствуют')
else:
    response_df_detail = response_df_detail.drop(['user_id', 'transaction_id'], axis=1)
    response_df_detail['transaction_type'] = response_df_detail['transaction_type'].replace({'add': 'Пополнение', 'deduct': 'Списание'})
    columns_names = {'transaction_type': 'Тип транзакции',
                    'amount': 'Сумма'}
    response_df_detail = response_df_detail.rename(columns=columns_names)
    response_df_detail = response_df_detail.set_index(np.arange(1, len(response_df_detail)+1))
    st.dataframe(response_df_detail)
