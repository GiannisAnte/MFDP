import streamlit as st
import pandas as pd

# Симулируем базу данных (замените на ваше реальное соединение с базой данных)
user_data = {}  # Храним информацию о пользователях (имя пользователя, пароль, баланс)
transactions = []  # Храним историю транзакций

# --- Вход/Регистрация ---

def login_register():
    st.title("Вход/Регистрация")

    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type='password')
        login_button = st.form_submit_button("Войти")
        if login_button:
            # if username in user_data and user_data[username]['password'] == password:
            if True:
                st.success(f"Добро пожаловать, {username}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            else:
                st.error("Неверное имя пользователя или пароль")

    with st.form("register_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type='password')
        confirm_password = st.text_input("Подтвердите пароль", type='password')
        register_button = st.form_submit_button("Зарегистрироваться")
        if register_button:
            if username not in user_data:
                if password == confirm_password:
                    user_data[username] = {'password': password, 'balance': 0}
                    st.success("Регистрация прошла успешно!")
                    st.experimental_rerun()
                else:
                    st.error("Пароли не совпадают!")
            else:
                st.error("Имя пользователя уже существует")

# --- Главная Страница ---

def main_page():
    st.title(f"Добро пожаловать, {st.session_state.username}!")
    
    # Отображаем баланс пользователя
    balance = 100
    st.write(f"Ваш баланс: ${balance}")
    
    # Кнопки для действий
    with st.form("top_up_form"):
        top_up_amount = st.number_input("Введите сумму", min_value=1, step=1)
        submit_button = st.form_submit_button("Подтвердить")
        if submit_button:
            user_data[st.session_state.username]['balance'] += top_up_amount
            transactions.append({
                'username': st.session_state.username,
                'type': 'Пополнение',
                'amount': top_up_amount,
                'timestamp': pd.Timestamp.now()
            })
            st.success("Баланс пополнен!")
            st.experimental_rerun()

    with st.form("transactions_form"):
        view_transactions_button = st.form_submit_button("Просмотреть транзакции")
        if view_transactions_button:
            user_transactions = [t for t in transactions if t['username'] == st.session_state.username]
            if user_transactions:
                df = pd.DataFrame(user_transactions)
                st.dataframe(df)
            else:
                st.write("Транзакций пока нет.")

    with st.form("transaction_form"):
        make_transaction_button = st.form_submit_button("Сделать транзакцию")
        if make_transaction_button:
            st.write("**Еще не реализовано**")

    if st.button("Прогноз"):
        st.session_state['show_prediction'] = True

# --- Страница Прогноза ---

def prediction_page():
    st.title("Прогноз")

    # Боковая панель для параметров прогнозирования
    with st.sidebar:
        st.header("Параметры прогнозирования")
        # Добавьте свои параметры прогнозирования здесь (например, выбор признаков, тип модели)

    # Отображаем результаты прогнозирования
    st.write("**Результаты прогнозирования будут показаны здесь.**")

    if st.button("Назад к главной"):
        st.session_state['show_prediction'] = False
        st.experimental_rerun()

# --- Основной Streamlit App ---

if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.session_state['show_prediction'] = False  # Инициализируем show_prediction

    if not st.session_state.logged_in:
        login_register()
    else:
        if st.session_state.show_prediction:
            prediction_page()
        else:
            main_page() 