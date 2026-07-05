from cachetools import TTLCache

weather_cache = TTLCache(maxsize=500, ttl=300)
forecast_cache = TTLCache(maxsize=500, ttl=600)