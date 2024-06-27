class User:
    def __init__(self, user_id: int, username: str, password: str, email: str,
                 first_name: str, last_name: str, balance: float, role: str):
        self.__id = user_id
        self.__username = username
        self.__password = password
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

    @balance.setter
    def balance(self, value: float):
        self.__balance = value

    def deduct_balance(self, amount):
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        return False

    def history(self, action):
        self.__activity_history[action] = self.__balance
