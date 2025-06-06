import requests

def get_hourly_weather(latitude: float,
                       longitude: float,
                       hours_ahead: int = 0) -> dict:
    """
    Получает прогноз погоды от Open-Meteo на указанный час вперёд.
    Возвращает значения с заменой None на понятные дефолты.
    """
    MAX_HOURS = 16 * 24
    if hours_ahead < 0 or hours_ahead > MAX_HOURS:
        raise ValueError(f"hours_ahead должно быть от 0 до {MAX_HOURS}")

    hourly_params = [
        "temperature_2m",
        "temperature_10m",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m"
    ]
    hourly_str = ",".join(hourly_params)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&hourly={hourly_str}"
        f"&forecast_days=16"
        f"&timezone=auto"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        times = data["hourly"]["time"]
        if hours_ahead >= len(times):
            return None

        idx = hours_ahead

        # Понятные значения по умолчанию
        fallback = {
            "temperature_2m": "Отсутствует",
            "temperature_10m": "Отсутствует",
            "wind_speed_10m": "Отсутствует",
            "wind_direction_10m": "Отсутствует",
            "wind_gusts_10m": "Отсутствует"
        }

        def safe_get(param):
            values = data["hourly"].get(param, [])
            return values[idx] if idx < len(values) and values[idx] is not None else fallback[param]

        result = {
            "time": times[idx],
            "temperature_2m": safe_get("temperature_2m"),
            "temperature_10m": safe_get("temperature_10m"),
            "wind_speed_10m": safe_get("wind_speed_10m"),
            "wind_direction_10m": safe_get("wind_direction_10m"),
            "wind_gusts_10m": safe_get("wind_gusts_10m")
        }
        return result

    except requests.RequestException as e:
        print(f"Ошибка при запросе к Open-Meteo: {e}")
        return None
