from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session
# from database.config import get_settings
# from models.user import User
from services.user_service import create_user, get_user, get_all_users, authenticate, add_to_balance, deduct_from_balance, get_balance
from services.transaction_service import tr_history
from database.database import get_session, init_db, engine


if __name__ == "__main__":

    test_user_1 = ('test_user_1', 'test1@mail.ru', 'test1')
    test_user_2 = ('test_user_2', 'test2@mail.ru', 'test2')
    test_user_3 = ('test_user_3', 'test3@mail.ru', 'test3')

    init_db()


    with Session(engine) as session:
        # Создание пользователей
        print('Создание пользователей')
        create_user(*test_user_1, session)
        create_user(*test_user_2, session)
        create_user(*test_user_3, session)
        users = get_all_users(session)
    for user in users:
        print(f'id: {user.id} - {user.email}')

    # Аутентификация
    print('Аутентификация')
    auth = []
    for user in users:
        auth.append(authenticate(user.username, 'test1', session))
    print(auth)

    # Пополнение и уменьшение
    print('Пополнение и уменьшение баланса')
    print(f'1 - {get_balance(1, session)}, 2 - {get_balance(2, session)}, 3 - {get_balance(3, session)}')

    add_to_balance(3, 12.0, session)
    print(f'1 - {get_balance(1, session)}, 2 - {get_balance(2, session)}, 3 - {get_balance(3, session)}')

    deduct_from_balance(1, 15.0, session)
    print(f'1 - {get_balance(1, session)}, 2 - {get_balance(2, session)}, 3 - {get_balance(3, session)}')

    # Запрос истории действий
    print('Запрос истории действий юзера с id=1')
    print(tr_history(1, session))

    

    



