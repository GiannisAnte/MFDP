from pydantic import BaseModel, Field, field_validator, ValidationError

class Tasks(BaseModel):
    action_id: int
    user_id: int
    username: str
    amount: int
    input_data: str
    response: str