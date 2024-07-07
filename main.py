from database.config import get_settings
from database.database import get_session, init_db, engine
from app.services.user_service import create_user
from sqlmodel import Session
from app.models.user import User


if __name__ == "__main__":
    test_user_1 = User(email='test1@mail.ru', password='test1')
    test_user_2 = User(email='test2@mail.ru', password='test2')
    test_user_3 = User(email='test3@mail.ru', password='test3')

    # settings = get_settings()
    # print(settings.DB_HOST)
    # print(settings.DB_NAME)

    init_db()
    print('Init db has been success')

    with Session(engine) as session:
        create_user(test_user_1, session)
        create_user(test_user_2, session)
        create_user(test_user_3, session)
        # users = get_all_users(session)

    # for user in users:
    #     print(f'id: {user.id} - {user.email}')