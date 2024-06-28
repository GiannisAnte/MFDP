class Balance:
    def __init__(self, user, amount):
        self.__user = user
        self.__amount = amount

    @property
    def user(self):
        return self.__user

    @property
    def amount(self):
        return self.__amount

    def add_balance(self):
        self.__user.add_balance(self.__amount)

    def deduct_amount(self, amount: float) -> None:
        if amount > self.__balance:
            raise ValueError("Недостаточно средств")
        self.__balance -= amount
