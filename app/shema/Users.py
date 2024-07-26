from pydantic import BaseModel, Field, field_validator, ValidationError

class Users(BaseModel):
    id: int
    username: str
    password: str
    email: str
    balance: int