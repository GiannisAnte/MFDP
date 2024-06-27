from datetime import datetime

from app.models.user import User


class Transaction:
    """transaction_type - пополнение или списание"""
    def __init__(self, transaction_id: int, user_id: int, amount: float, transaction_time: datetime,
                 transaction_type: str):
        self.__id = transaction_id
        self.__user_id = user_id
        self.__amount = amount
        self.__time = transaction_time
        self.__type = transaction_type

