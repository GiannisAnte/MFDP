import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

def get_daily_weather(
    latitude: float,
    longitude: float,
    date: Optional[str] = None,
    forecast: Optional[int] = None,
    timezone: str = "auto"
) -> Dict[str, Any]:
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        base_date = datetime.utcnow().date()
        forecast = forecast or 0
        target_date = base_date + timedelta(days=forecast)

    date_str = target_date.isoformat()

    daily_fields = [
        "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
        "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
        "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours",
        "relative_humidity_2m_max", "relative_humidity_2m_min", "relative_humidity_2m_mean",
        "dew_point_2m_max", "dew_point_2m_min", "dew_point_2m_mean",
        "wind_speed_10m_max", "wind_speed_10m_min", "wind_speed_10m_mean",
        "wind_gusts_10m_max", "wind_gusts_10m_mean", "wind_direction_10m_dominant",
        "sunshine_duration", "daylight_duration", "shortwave_radiation_sum",
        "pressure_msl_max", "pressure_msl_min", "pressure_msl_mean", "weather_code",
        "et0_fao_evapotranspiration"
    ]

    base_url = (
        "https://api.open-meteo.com/v1/forecast"
        if target_date >= datetime.utcnow().date()
        else "https://archive-api.open-meteo.com/v1/archive"
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join(daily_fields),
        "timezone": timezone,
        "start_date": date_str,
        "end_date": date_str
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    daily = data.get("daily", {})
    if not daily or "time" not in daily or len(daily["time"]) == 0:
        return {
            "Невалидный день": date_str,
            "Отсутствуют признаки": daily_fields
        }

    index = 0
    result = {field: daily.get(field, [None])[index] for field in daily_fields}

    # Заполнение *_mean по min/max
    for prefix in [
        "temperature_2m", "apparent_temperature", "relative_humidity_2m",
        "dew_point_2m", "wind_speed_10m", "pressure_msl"
    ]:
        max_key = f"{prefix}_max"
        min_key = f"{prefix}_min"
        mean_key = f"{prefix}_mean"
        if result.get(mean_key) is None and result.get(min_key) is not None and result.get(max_key) is not None:
            result[mean_key] = (result[max_key] + result[min_key]) / 2

    # Проверка на отсутствующие признаки
    missing = [key for key, value in result.items() if value is None]
    if missing:
        return {
            "Невалидный день": date_str,
            "Отсутствуют признаки": missing
        }

    # если всё в порядке — возвращаем результат + дату и координаты
    return {
        **result,
        "lat": latitude,
        "lon": longitude,
        "date": date_str
    }
