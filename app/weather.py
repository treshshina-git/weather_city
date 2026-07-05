import requests
from app.cache import weather_cache, forecast_cache
from app.config import WEATHER_API_KEY


def safe_get(url, params):
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def get_weather(city):
    key = f"w:{city}"
    if key in weather_cache:
        return weather_cache[key]

    data = safe_get(
        "https://api.openweathermap.org/data/2.5/weather",
        {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "ru"
        }
    )

    if not data:
        return None

    result = {
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels": data["main"]["feels_like"],
        "pressure": data["main"]["pressure"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "code": data["weather"][0]["id"]
    }

    weather_cache[key] = result
    return result


def get_forecast(city):
    key = f"f:{city}"
    if key in forecast_cache:
        return forecast_cache[key]

    data = safe_get(
        "https://api.openweathermap.org/data/2.5/forecast",
        {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "ru"
        }
    )

    if not data:
        return None

    days = {}

    for i in data["list"]:
        day = i["dt_txt"].split(" ")[0]
        days.setdefault(day, []).append(i["main"]["temp"])

    result = [
        {"day": k, "temp": round(sum(v)/len(v), 1)}
        for k, v in list(days.items())[:5]
    ]

    forecast_cache[key] = result
    return result