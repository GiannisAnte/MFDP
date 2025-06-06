from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.hourly_weather import get_hourly_weather
from models.prediction import Prediction
from database.database import engine, create_session
from uuid import UUID

router_weather = APIRouter(prefix="/weather", tags=["Weather"])
router_h_weather = APIRouter(tags=["Weather"])

@router_weather.get("/forecast-hourly/")
async def forecast_hourly(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    hours_ahead: int = Query(0, ge=0, le=384, description="Через сколько часов получить прогноз (макс. 384 часа = 16 суток)")
):
    """
    Возвращает погодный прогноз на указанное число часов вперёд.
    """
    try:
        forecast = get_hourly_weather(lat, lon, hours_ahead)
        return forecast
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении прогноза: {e}")
    

@router_h_weather.get("/predictions/{event_id}")
def get_prediction(event_id: UUID):
    with create_session() as session:
        prediction = session.query(Prediction).filter_by(fire_event_id=event_id).first()
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return prediction