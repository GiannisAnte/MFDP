import streamlit as st
import requests
import pandas as pd
import json
import numpy as np
from extra_streamlit_components import CookieManager
import settings

COOKIE_NAME = settings.COOKIE_NAME

st.title("История предсказаний")

cookie_manager = CookieManager()
access_token = cookie_manager.get(COOKIE_NAME)  # имя cookie должно совпадать с серверным COOKIE_NAME

if not access_token:
    st.error("Вы не авторизованы. Пожалуйста, войдите.")
    if st.button("⬅ Назад к авторизации"):
                st.switch_page("Home.py")
    st.stop()

# Отправляем запрос с cookie, а не с заголовком Authorization
cookies = { COOKIE_NAME: access_token }

try:
    response = requests.get(
        'http://app:8080/user/history',
        cookies=cookies  # Вот здесь передаем cookie
    )

    if response.status_code == 200:
        data = response.json()

        if not data:
            st.success("История запросов отсутствует.")
            if st.button("⬅ Назад в личный кабинет"):
                st.switch_page("pages/cab.py")
            st.stop()

        # Обрабатываем данные
        for item in data:
            payload = item.get("payload", {})
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except:
                    payload = {}

            image_path = payload.get("image_path", "")
            filename = payload.get("original_filename", "image.jpg")
            full_url = f"http://app:8080/{image_path}" if image_path else ""

            # HTML с hover-превью
            item["image_html"] = f"""
                <div style="position: relative; display: inline-block;">
                    <span style="cursor: pointer; text-decoration: underline; color: blue;">
                        {filename}
                    </span>
                    <div style="
                        display: none;
                        position: absolute;
                        top: 20px;
                        left: 0;
                        z-index: 10;
                        border: 1px solid #ccc;
                        background-color: white;
                        padding: 5px;
                    " class="img-preview">
                        <img src="{full_url}" style="width: 200px;"/>
                    </div>
                </div>
            """

        df = pd.DataFrame(data)

        rename_columns = {
            "fire_event_id": "ID события",
            "source": "Источник",
            "latitude": "Широта",
            "longitude": "Долгота",
            "variant": "Вариант модели",
            "result": "Результат",
            "score": "Оценка",
            "image_html": "Изображение"
        }

        df = df.rename(columns=rename_columns)
        df.index = range(1, len(df) + 1)

        # HTML-таблица с hover preview
        table_html = """
        <style>
            .img-preview {
                display: none;
            }
            div:hover > .img-preview {
                display: block;
            }
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
                vertical-align: top;
            }
        </style>
        <table>
            <thead><tr>
        """
        for col in df.columns:
            table_html += f"<th>{col}</th>"
        table_html += "</tr></thead><tbody>"

        for _, row in df.iterrows():
            table_html += "<tr>"
            for col in df.columns:
                val = row[col]
                if col == "Изображение":
                    table_html += f"<td>{val}</td>"
                else:
                    table_html += f"<td>{val}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"

        st.markdown(table_html, unsafe_allow_html=True)

    else:
        st.error(f"Ошибка при получении истории: {response.status_code} — {response.text}")

except Exception as e:
    st.error(f"Ошибка при загрузке истории: {str(e)}")

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("⬅ Назад в личный кабинет"):
        st.switch_page("pages/cab.py")

# try:
#     response = requests.get(
#         'http://app:8080/user/history',
#         headers={"Authorization": f"Bearer {access_token}"}
#     )

#     if response.status_code == 200:
#         data = response.json()

#         if not data or len(data) == 0:
#             st.success("История запросов отсутствует.")
#         else:
#             # Преобразуем в DataFrame
#             df = pd.DataFrame(data)

#             # Преобразуем поля, если нужно
#             if 'payload' in df.columns:
#                 df['payload'] = df['payload'].apply(lambda x: json.dumps(x, ensure_ascii=False))

#             rename_columns = {
#                 "fire_event_id": "ID события",
#                 "source": "Источник",
#                 "latitude": "Широта",
#                 "longitude": "Долгота",
#                 "payload": "Доп. данные",
#                 "variant": "Вариант модели",
#                 "result": "Результат",
#                 "score": "Оценка"
#             }

#             df.rename(columns=rename_columns, inplace=True)
#             df.index = range(1, len(df) + 1)  # Индексация с 1

#             st.dataframe(df, use_container_width=True)
#     else:
#         st.error(f"Ошибка при получении истории: {response.status_code} — {response.text}")

# except Exception as e:
#     st.error(f"Ошибка при загрузке истории: {str(e)}")
