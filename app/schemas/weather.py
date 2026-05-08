from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


class CurrentWeather(BaseModel):
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    temperature: float
    apparent_temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    precipitation: float
    snowfall: float
    cloud_cover: float
    pressure: float
    weather_code: int
    weather_description: str
    is_day: int
    fetched_at: datetime


class ForecastDay(BaseModel):
    forecast_date: date
    temp_max: float
    temp_min: float
    precipitation_sum: float
    snowfall_sum: float
    wind_speed_max: float
    wind_gusts_max: float
    weather_code: int
    weather_description: str
    sunrise: Optional[str]
    sunset: Optional[str]
    uv_index_max: Optional[float]


class ForecastResponse(BaseModel):
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    days: List[ForecastDay]


class WeatherAlert(BaseModel):
    level: str           # "warning" | "watch" | "advisory"
    type: str            # "wind" | "rain" | "heat" | "cold" | "snow"
    message: str
    value: float
    threshold: float
    unit: str


class AlertsResponse(BaseModel):
    city_name: str
    country_code: Optional[str]
    alerts: List[WeatherAlert]
    checked_at: datetime


class StatsSummary(BaseModel):
    city_name: str
    country_code: Optional[str]
    period_days: int
    temp_avg: Optional[float]
    temp_max: Optional[float]
    temp_min: Optional[float]
    temp_std: Optional[float]
    humidity_avg: Optional[float]
    wind_speed_avg: Optional[float]
    wind_speed_max: Optional[float]
    precipitation_total: Optional[float]
    most_common_condition: Optional[str]
    records_count: int


class CityCompareItem(BaseModel):
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    temperature: float
    apparent_temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    weather_description: str


class CompareResponse(BaseModel):
    cities: List[CityCompareItem]
    compared_at: datetime
    warmest: str
    coldest: str
    most_humid: str
    windiest: str
