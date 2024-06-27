from datetime import datetime


class Prediction:
    def __init__(self, id, user_id, model_id, data, result, cost, timestamp=datetime.now()):
        self.__id = id
        self.__user_id = user_id
        self.__model_id = model_id
        self.__data = data
        self.__cost = cost
        self.__result = result
        self.__time = timestamp
