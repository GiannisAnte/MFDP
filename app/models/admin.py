from app.models.user import User
from app.models.transaction import Transaction


class Admin(User):
    def __init__(self, user_id: int, username: str, password: str, email: str, balance: float):
        super().__init__(user_id, username, password, email, balance, role="admin")

    def transactions_history(self, transactions: list[Transaction]) -> list[Transaction]:
        return transactions
