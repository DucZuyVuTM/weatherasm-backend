from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class UserEntity:
    id: Optional[int]
    email: str
    username: str
    hashed_password: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LocationEntity:
    id: Optional[int]
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float


@dataclass
class SavedLocationEntity:
    id: Optional[int]
    user_id: int
    location_id: int
    location: Optional[LocationEntity] = None
    created_at: Optional[datetime] = None


@dataclass
class WeatherRecordEntity:
    id: Optional[int]
    location_id: int
    temperature: Optional[float]
    apparent_temperature: Optional[float]
    humidity: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    precipitation: Optional[float]
    snowfall: Optional[float]
    cloud_cover: Optional[float]
    pressure: Optional[float]
    weather_code: Optional[int]
    weather_description: Optional[str]
    is_day: Optional[int]
    fetched_at: Optional[datetime]
    location: Optional[LocationEntity] = None


@dataclass
class ForecastDayEntity:
    forecast_date: date
    temp_max: Optional[float]
    temp_min: Optional[float]
    precipitation_sum: float
    snowfall_sum: float
    wind_speed_max: Optional[float]
    wind_gusts_max: Optional[float]
    weather_code: Optional[int]
    weather_description: Optional[str]
    sunrise: Optional[str]
    sunset: Optional[str]
    uv_index_max: Optional[float]


@dataclass
class ForecastEntity:
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    days: List[ForecastDayEntity] = field(default_factory=list)


@dataclass
class WeatherAlert:
    level: str
    type: str
    message: str
    value: float
    threshold: float
    unit: str


@dataclass
class WeatherStatsEntity:
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
