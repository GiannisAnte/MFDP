from models.action import Action


def action_log(request: Action, session) -> None:
    """Запись действия в БД"""
    session.add(request)
    session.commit()
    session.refresh(request)


def act_history(user_id: int, session) -> list[Action]:
    """История действий"""
    req_history = (session.query(Action)
                   .where(Action.user_id == user_id)
                   .all())
    return req_history


