from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.infrastructure.repositories import (
    SqlLocationRepository, SqlWeatherRecordRepository,
)
from app.infrastructure.external.open_meteo import OpenMeteoGateway
from app.application.dto import (
    CurrentWeatherDTO, ForecastResponseDTO, AlertsResponseDTO,
    StatsSummaryDTO, CompareResponseDTO, WeatherAlertDTO,
)
from app.application.mappers import (
    weather_record_to_dto, forecast_to_dto, alert_to_dto,
    stats_to_dto, compare_result_to_dto,
)
from app.domain.use_cases import (
    GetCurrentWeatherUseCase, GetForecastUseCase,
    GetAlertsUseCase, CompareCitiesUseCase,
)
from app.domain.entities import UserEntity
from app.presentation.dependencies import get_current_user, get_weather_gateway

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current", response_model=CurrentWeatherDTO)
async def get_current(
    city: str = Query(..., description="City name, e.g. 'Vilnius'"),
    db: Session = Depends(get_db),
    _: UserEntity = Depends(get_current_user),
    gateway: OpenMeteoGateway = Depends(get_weather_gateway),
):
    use_case = GetCurrentWeatherUseCase(
        SqlLocationRepository(db), SqlWeatherRecordRepository(db), gateway
    )
    record = await use_case.execute(city)
    return weather_record_to_dto(record)


@router.get("/forecast", response_model=ForecastResponseDTO)
async def get_forecast(
    city: str = Query(...),
    days: int = Query(7, ge=1, le=16),
    _: UserEntity = Depends(get_current_user),
    gateway: OpenMeteoGateway = Depends(get_weather_gateway),
):
    forecast = await GetForecastUseCase(gateway).execute(city, days)
    return forecast_to_dto(forecast)


@router.get("/alerts", response_model=AlertsResponseDTO)
async def get_alerts(
    city: str = Query(...),
    include_forecast: bool = Query(True),
    _: UserEntity = Depends(get_current_user),
    gateway: OpenMeteoGateway = Depends(get_weather_gateway),
):
    result = await GetAlertsUseCase(gateway).execute(city, include_forecast)
    return AlertsResponseDTO(
        city_name=result["city_name"],
        country_code=result["country_code"],
        alerts=[alert_to_dto(a) for a in result["alerts"]],
        checked_at=result["checked_at"],
    )


@router.get("/history", response_model=List[CurrentWeatherDTO])
def get_history(
    city: str = Query(...),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserEntity = Depends(get_current_user),
):
    records = SqlWeatherRecordRepository(db).find_by_city(city, limit)
    return [weather_record_to_dto(r) for r in records]


@router.get("/analysis", response_model=StatsSummaryDTO)
def get_analysis(
    city: str = Query(...),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _: UserEntity = Depends(get_current_user),
):
    stats = SqlWeatherRecordRepository(db).compute_stats(city, days)
    return stats_to_dto(stats)


@router.get("/compare", response_model=CompareResponseDTO)
async def compare_cities(
    cities: str = Query(..., description="Comma-separated city names"),
    db: Session = Depends(get_db),
    _: UserEntity = Depends(get_current_user),
    gateway: OpenMeteoGateway = Depends(get_weather_gateway),
):
    city_list = [c.strip() for c in cities.split(",") if c.strip()]
    if len(city_list) < 2:
        raise HTTPException(400, "Provide at least 2 cities to compare")
    if len(city_list) > 10:
        raise HTTPException(400, "Maximum 10 cities per comparison")
    result = await CompareCitiesUseCase(
        SqlLocationRepository(db), SqlWeatherRecordRepository(db), gateway
    ).execute(city_list)
    return compare_result_to_dto(result)
