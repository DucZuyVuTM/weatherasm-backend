from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ── User ───────────────────────────────────────────────────────────────────────

class UserCreateDTO(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores/hyphens allowed)")
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be 3–30 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdateDTO(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponseDTO(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequestDTO(BaseModel):
    refresh_token: str


class PasswordChangeDTO(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


# ── Location ───────────────────────────────────────────────────────────────────

class LocationCreateDTO(BaseModel):
    city_name: str


class LocationResponseDTO(BaseModel):
    id: int
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Weather ────────────────────────────────────────────────────────────────────

class CurrentWeatherDTO(BaseModel):
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


class ForecastDayDTO(BaseModel):
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


class ForecastResponseDTO(BaseModel):
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    days: List[ForecastDayDTO]


class WeatherAlertDTO(BaseModel):
    level: str
    type: str
    message: str
    value: float
    threshold: float
    unit: str


class AlertsResponseDTO(BaseModel):
    city_name: str
    country_code: Optional[str]
    alerts: List[WeatherAlertDTO]
    checked_at: datetime


class StatsSummaryDTO(BaseModel):
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


class CityCompareItemDTO(BaseModel):
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


class CompareResponseDTO(BaseModel):
    cities: List[CityCompareItemDTO]
    compared_at: datetime
    warmest: str
    coldest: str
    most_humid: str
    windiest: str
