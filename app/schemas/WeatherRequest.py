from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class WeatherRequest(BaseModel):
    user_id: UUID = Field(..., description="UUID пользователя")
    latitude: float = Field(..., description="Широта")
    longitude: float = Field(..., description="Долгота")
    date: Optional[str] = Field(None, description="Дата в формате YYYY-MM-DD")
    forecast: Optional[int] = Field(None, description="Смещение в днях от сегодня")
    customer: str = Field(..., description="cb_xgb или cb_rf")
