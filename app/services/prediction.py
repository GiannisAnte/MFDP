from datetime import datetime


class Prediction:
    def __init__(self, id, user, model, data, result, cost, timestamp=datetime.now()):
        self.__id = id
        self.__user = user
        self.__model = model
        self.__data = data
        self.__cost = cost
        self.__result = result
        self.__time = timestamp

    @property
    def user(self):
        return self.__user

    @property
    def ml_model(self):
        return self.__model

    @property
    def data(self):
        return self.__data

    @property
    def result(self):
        return self.__result

    @property
    def timestamp(self):
        return self.__time

    def make_prediction(self):
        self.__result = self.__model.predict(self.__data)
        self.__time = datetime.now()

    def get_predictions_by_user(user_id):
        """
        Возврат список предсказаний для пользователя по его ID.
        """
        ...

