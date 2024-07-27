from pydantic import BaseModel, Field, field_validator, ValidationError

class Transactions(BaseModel):
    id: int
    user_id: int
    username: str
    transaction_type: str
    amount: int