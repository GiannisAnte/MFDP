from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class Users(BaseModel):
    id: UUID
    username: str
    # password: str
    email: EmailStr
    is_superuser : bool
    created_at: datetime