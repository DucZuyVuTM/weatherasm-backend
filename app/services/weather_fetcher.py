import httpx
from datetime import datetime, timezone
from typing import Optional, Tuple
from fastapi import HTTPException

from app.core.config import OPEN_METEO_BASE_URL, GEOCODING_BASE_URL

# WMO Weather interpretation codes
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


async def geocode_city(city_name: str) -> Tuple[float, float, str, Optional[str]]:
    """Return (lat, lon, resolved_name, country_code) for a city string."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{GEOCODING_BASE_URL}/search",
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
        )
    if resp.status_code != 200:
        raise HTTPException(502, "Geocoding service unavailable")
    data = resp.json()
    results = data.get("results")
    if not results:
        raise HTTPException(404, f"City '{city_name}' not found")
    r = results[0]
    return r["latitude"], r["longitude"], r.get("name", city_name), r.get("country_code")


async def fetch_current_weather(lat: float, lon: float, city_name: str, country_code: Optional[str]) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m", "apparent_temperature", "relative_humidity_2m",
            "wind_speed_10m", "wind_direction_10m", "precipitation",
            "snowfall", "cloud_cover", "surface_pressure",
            "weather_code", "is_day",
        ],
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
    if resp.status_code != 200:
        raise HTTPException(502, "Weather service unavailable")
    data = resp.json()
    c = data["current"]
    code = c.get("weather_code", 0)
    return {
        "city_name": city_name,
        "country_code": country_code,
        "latitude": lat,
        "longitude": lon,
        "temperature": c.get("temperature_2m"),
        "apparent_temperature": c.get("apparent_temperature"),
        "humidity": c.get("relative_humidity_2m"),
        "wind_speed": c.get("wind_speed_10m"),
        "wind_direction": c.get("wind_direction_10m"),
        "precipitation": c.get("precipitation"),
        "snowfall": c.get("snowfall"),
        "cloud_cover": c.get("cloud_cover"),
        "pressure": c.get("surface_pressure"),
        "weather_code": code,
        "weather_description": WMO_CODES.get(code, "Unknown"),
        "is_day": c.get("is_day"),
        "fetched_at": datetime.now(timezone.utc),
    }


async def fetch_forecast(lat: float, lon: float, city_name: str, country_code: Optional[str], days: int = 7) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "snowfall_sum",
            "wind_speed_10m_max", "wind_gusts_10m_max",
            "weather_code", "sunrise", "sunset", "uv_index_max",
        ],
        "forecast_days": days,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
    if resp.status_code != 200:
        raise HTTPException(502, "Forecast service unavailable")
    data = resp.json()
    d = data["daily"]
    forecast_days = []
    for i in range(len(d["time"])):
        code = d["weather_code"][i]
        forecast_days.append({
            "forecast_date": d["time"][i],
            "temp_max": d["temperature_2m_max"][i],
            "temp_min": d["temperature_2m_min"][i],
            "precipitation_sum": d["precipitation_sum"][i] or 0.0,
            "snowfall_sum": d["snowfall_sum"][i] or 0.0,
            "wind_speed_max": d["wind_speed_10m_max"][i],
            "wind_gusts_max": d["wind_gusts_10m_max"][i],
            "weather_code": code,
            "weather_description": WMO_CODES.get(code, "Unknown"),
            "sunrise": d["sunrise"][i],
            "sunset": d["sunset"][i],
            "uv_index_max": d.get("uv_index_max", [None] * (i + 1))[i],
        })
    return {
        "city_name": city_name,
        "country_code": country_code,
        "latitude": lat,
        "longitude": lon,
        "days": forecast_days,
    }
