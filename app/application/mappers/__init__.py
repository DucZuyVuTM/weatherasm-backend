from app.domain.entities import (
    UserEntity, SavedLocationEntity, WeatherRecordEntity,
    ForecastEntity, WeatherAlert, WeatherStatsEntity,
)
from app.application.dto import (
    UserResponseDTO, LocationResponseDTO, CurrentWeatherDTO,
    ForecastResponseDTO, ForecastDayDTO, WeatherAlertDTO,
    AlertsResponseDTO, StatsSummaryDTO, CityCompareItemDTO, CompareResponseDTO,
)
from datetime import datetime
from typing import List


def user_to_dto(entity: UserEntity) -> UserResponseDTO:
    return UserResponseDTO(
        id=entity.id, email=entity.email, username=entity.username,
        full_name=entity.full_name, role=entity.role,
        is_active=entity.is_active, created_at=entity.created_at,
    )


def saved_location_to_dto(entity: SavedLocationEntity) -> LocationResponseDTO:
    loc = entity.location
    return LocationResponseDTO(
        id=entity.id, city_name=loc.city_name, country_code=loc.country_code,
        latitude=loc.latitude, longitude=loc.longitude, created_at=entity.created_at,
    )


def weather_record_to_dto(entity: WeatherRecordEntity) -> CurrentWeatherDTO:
    loc = entity.location
    return CurrentWeatherDTO(
        city_name=loc.city_name if loc else "",
        country_code=loc.country_code if loc else None,
        latitude=loc.latitude if loc else 0,
        longitude=loc.longitude if loc else 0,
        temperature=entity.temperature or 0,
        apparent_temperature=entity.apparent_temperature or 0,
        humidity=entity.humidity or 0,
        wind_speed=entity.wind_speed or 0,
        wind_direction=entity.wind_direction or 0,
        precipitation=entity.precipitation or 0,
        snowfall=entity.snowfall or 0,
        cloud_cover=entity.cloud_cover or 0,
        pressure=entity.pressure or 0,
        weather_code=entity.weather_code or 0,
        weather_description=entity.weather_description or "",
        is_day=entity.is_day or 1,
        fetched_at=entity.fetched_at,
    )


def forecast_to_dto(entity: ForecastEntity) -> ForecastResponseDTO:
    return ForecastResponseDTO(
        city_name=entity.city_name, country_code=entity.country_code,
        latitude=entity.latitude, longitude=entity.longitude,
        days=[
            ForecastDayDTO(
                forecast_date=d.forecast_date,
                temp_max=d.temp_max or 0, temp_min=d.temp_min or 0,
                precipitation_sum=d.precipitation_sum, snowfall_sum=d.snowfall_sum,
                wind_speed_max=d.wind_speed_max or 0, wind_gusts_max=d.wind_gusts_max or 0,
                weather_code=d.weather_code or 0,
                weather_description=d.weather_description or "",
                sunrise=d.sunrise, sunset=d.sunset, uv_index_max=d.uv_index_max,
            )
            for d in entity.days
        ],
    )


def alert_to_dto(entity: WeatherAlert) -> WeatherAlertDTO:
    return WeatherAlertDTO(
        level=entity.level, type=entity.type, message=entity.message,
        value=entity.value, threshold=entity.threshold, unit=entity.unit,
    )


def stats_to_dto(entity: WeatherStatsEntity) -> StatsSummaryDTO:
    return StatsSummaryDTO(**entity.__dict__)


def compare_result_to_dto(result: dict) -> CompareResponseDTO:
    return CompareResponseDTO(
        cities=[
            CityCompareItemDTO(
                city_name=r.location.city_name, country_code=r.location.country_code,
                latitude=r.location.latitude, longitude=r.location.longitude,
                temperature=r.temperature or 0, apparent_temperature=r.apparent_temperature or 0,
                humidity=r.humidity or 0, wind_speed=r.wind_speed or 0,
                precipitation=r.precipitation or 0,
                weather_description=r.weather_description or "",
            )
            for r in result["cities"]
        ],
        compared_at=result["compared_at"],
        warmest=result["warmest"], coldest=result["coldest"],
        most_humid=result["most_humid"], windiest=result["windiest"],
    )
