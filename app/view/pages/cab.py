import streamlit as st
from extra_streamlit_components import CookieManager
import requests
import settings

cookie_name = settings.COOKIE_NAME
cookie_manager = CookieManager()

# 1) берем токен из session_state ИЛИ из JS-куки
#    (важно: если вы нигде не кладёте в session_state["access_token"], 
#    то достаточно читать из cookie_manager)
token = st.session_state.get("access_token") or cookie_manager.get(cookie_name) or ""

# 2) проверяем, есть ли токен. Если нет — остановить рендер и показать сообщение
if not token:
    st.error("Необходима авторизация.")
    if st.button("⬅ Назад к авторизации"):
        st.switch_page("Home.py")
    st.stop()

# 3) Запросим у бэкенда имя пользователя
resp = requests.get(
    "http://app:8080/user/name", 
    cookies={cookie_name: token}
)
if resp.status_code == 200:
    # предполагаем, что бэкенд вернул {"username": "<имя>"}
    username = resp.json().get("username", "User")
else:
    username = "unlogged user"  # или можно сразу делать st.error и st.stop()

# 4) Выводим страницу кабинета
st.title("🔥 Личный кабинет")
st.header(f"Добро пожаловать, {username}!")

# 5) Кнопка “История запросов”
if st.button("История запросов"):
    st.switch_page("pages/history.py")

# 6) Выбор модели и переход
models = ["CNN", "CatBoost + XGBoost, F1-ориентированная модель", "CatBoost + RF, сбалансированная модель (Youden’s J)", "Ансамбль CNN и метеомодели"]
model = st.selectbox("Выберите модель для предсказания:", models)

page_map = {
    "CNN": "pages/cnn_page.py",
    "CatBoost + XGBoost, F1-ориентированная модель": "pages/cb_xgb_page.py",
    "CatBoost + RF, сбалансированная модель (Youden’s J)": "pages/cb_rf_page.py",
    "Ансамбль CNN и метеомодели": "pages/ensemble.py"
}

if st.button("Продолжить"):
    if model in page_map:
        st.session_state.selected_model = model
        st.switch_page(page_map[model])
    else:
        st.warning("Для выбранной модели страница пока не готова.")

# 7) Выход
if st.button("Выйти"):
    # 1) удаляем токен из session_state (если он там лежал)
    if "access_token" in st.session_state:
        del st.session_state["access_token"]

    # 2) удаляем JS-куку по правильному имени
    cookie_manager.delete(cookie_name)

    # 3) сообщаем об удачном логауте и переходим на Home
    st.success("Вы вышли из аккаунта.")
    st.switch_page("Home.py")

# import streamlit as st
# from extra_streamlit_components import CookieManager
# import requests
# import settings

# cookie_name = settings.COOKIE_NAME
# cookie_manager = CookieManager()

# token = st.session_state.get("access_token") or cookie_manager.get(cookie_name) or ""

# if not token:
#     st.error("Необходима авторизация.")
#     st.stop()

# st.title("Личный кабинет")


# resp = requests.get(
#     "http://app:8080/user/name",
#     cookies={cookie_name: token}
#     )
# if resp.status_code == 200:
#     username = resp.json().get("username", "User")
# else:
#     username = "unlogged user"

# st.title("🔥 Личный кабинет")
# st.header(f"Добро пожаловать, {username}!")

# if st.button("      История запросов        "):        
#     st.switch_page("pages/history.py")

# models = ["Linear Regression", "Random Forest", "CNN"]
# model = st.selectbox("Выберите модель для предсказания:", models)

# page_map = {
#     "CNN": "pages/cnn_page.py",
#     # "Linear Regression": "pages/linear.py",
#     # "Random Forest": "pages/random_forest.py"
# }

# if st.button("Продолжить"):
#     st.session_state.selected_model = model
#     st.switch_page(page_map[model])

# if st.button("Выйти"):
#     st.session_state.access_token = None
#     cookie_manager.delete("access_token")
#     st.experimental_rerun()