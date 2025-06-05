from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class HashPassword:
    """
    Класс для хеширования и верификации паролей с использованием bcrypt.
    """

    def create_hash(self, password: str) -> str:
        """Хеширует пароль."""
        return _pwd_context.hash(password)
    
    def verify_hash(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие открытого пароля и хешированного."""
        return _pwd_context.verify(plain_password, hashed_password)
