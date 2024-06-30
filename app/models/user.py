class User:
    def __init__(self, user_id: int, username: str, password: str, email: str,
                 first_name: str, last_name: str, balance: float, role: str):
        self.__id = user_id
        self.__username = username
        self.__password = password #hash_password
        self.__email = email
        self.__first_name = first_name
        self.__last_name = last_name
        self.__balance = balance
        self.__role = role
        self.__activity_history = {}

    @property
    def get_user_id(self):
        return self.__id

    @property
    def get_username(self):
        return self.__username

    @property
    def balance(self):
        return self.__balance

    def add_balance(self, amount):
        self.__balance += amount

    def history(self, action):
        self.__activity_history[action] = self.__balance
