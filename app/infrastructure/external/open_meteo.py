import httpx
from datetime import datetime, timezone
from typing import Optional
from app.core.config import OPEN_METEO_BASE_URL, GEOCODING_BASE_URL
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.domain.entities import LocationEntity, WeatherRecordEntity, ForecastEntity, ForecastDayEntity
from app.domain.repositories import IWeatherGateway

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


class OpenMeteoGateway(IWeatherGateway):
    def __init__(self, verify_ssl: bool = True):
        self._verify_ssl = verify_ssl

    async def geocode(self, city_name: str) -> LocationEntity:
        async with httpx.AsyncClient(timeout=10, verify=self._verify_ssl) as client:
            resp = await client.get(
                f"{GEOCODING_BASE_URL}/search",
                params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            )
        if resp.status_code != 200:
            raise ExternalServiceError("Geocoding service unavailable")
        results = resp.json().get("results")
        if not results:
            raise NotFoundError(f"City '{city_name}' not found")
        r = results[0]
        return LocationEntity(
            id=None,
            city_name=r.get("name", city_name),
            country_code=r.get("country_code"),
            latitude=r["latitude"],
            longitude=r["longitude"],
        )

    async def get_current(self, location: LocationEntity) -> WeatherRecordEntity:
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": [
                "temperature_2m", "apparent_temperature", "relative_humidity_2m",
                "wind_speed_10m", "wind_direction_10m", "precipitation",
                "snowfall", "cloud_cover", "surface_pressure", "weather_code", "is_day",
            ],
            "wind_speed_unit": "kmh",
            "timezone": "auto",
        }
        async with httpx.AsyncClient(timeout=15, verify=self._verify_ssl) as client:
            resp = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
        if resp.status_code != 200:
            raise ExternalServiceError("Weather service unavailable")
        c = resp.json()["current"]
        code = c.get("weather_code", 0)
        return WeatherRecordEntity(
            id=None, location_id=0,
            temperature=c.get("temperature_2m"),
            apparent_temperature=c.get("apparent_temperature"),
            humidity=c.get("relative_humidity_2m"),
            wind_speed=c.get("wind_speed_10m"),
            wind_direction=c.get("wind_direction_10m"),
            precipitation=c.get("precipitation"),
            snowfall=c.get("snowfall"),
            cloud_cover=c.get("cloud_cover"),
            pressure=c.get("surface_pressure"),
            weather_code=code,
            weather_description=WMO_CODES.get(code, "Unknown"),
            is_day=c.get("is_day"),
            fetched_at=datetime.now(timezone.utc),
        )

    async def get_forecast(self, location: LocationEntity, days: int = 7) -> ForecastEntity:
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
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
        async with httpx.AsyncClient(timeout=15, verify=self._verify_ssl) as client:
            resp = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
        if resp.status_code != 200:
            raise ExternalServiceError("Forecast service unavailable")
        d = resp.json()["daily"]
        forecast_days = []
        for i in range(len(d["time"])):
            code = d["weather_code"][i]
            forecast_days.append(ForecastDayEntity(
                forecast_date=d["time"][i],
                temp_max=d["temperature_2m_max"][i],
                temp_min=d["temperature_2m_min"][i],
                precipitation_sum=d["precipitation_sum"][i] or 0.0,
                snowfall_sum=d["snowfall_sum"][i] or 0.0,
                wind_speed_max=d["wind_speed_10m_max"][i],
                wind_gusts_max=d["wind_gusts_10m_max"][i],
                weather_code=code,
                weather_description=WMO_CODES.get(code, "Unknown"),
                sunrise=d["sunrise"][i],
                sunset=d["sunset"][i],
                uv_index_max=d.get("uv_index_max", [None] * (i + 1))[i],
            ))
        return ForecastEntity(
            city_name=location.city_name, country_code=location.country_code,
            latitude=location.latitude, longitude=location.longitude,
            days=forecast_days,
        )
