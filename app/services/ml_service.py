class PredictionTask:
    def __init__(self, task_id: int, user_id: int, model, data: list, amount: float):
        self.__task_id = task_id
        self.__user_id = user_id
        self.__model = model
        self.__data = data
        self.__amount = amount
        self.__result = None

    def get_task_id(self) -> int:
        return self.__task_id

    def get_user_id(self) -> int:
        return self.__user_id

    def get_model(self):
        return self.__model

    def get_data(self) -> list:
        return self.__data

    def get_cost(self) -> float:
        return self.__amount

    def execute(self) -> bool:
        # реализация выполнения задачи предсказания
        ...

    def validate_data(self, data: list) -> bool:
        # Проверка данных на ошибки
        return True

    def get_result(self):
        return self.__result