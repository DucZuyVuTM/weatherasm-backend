from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.weather_record import WeatherRecord
from app.schemas.weather import (
    CurrentWeather, ForecastResponse, AlertsResponse,
    StatsSummary, CompareResponse, CityCompareItem,
)
from app.core.security import get_current_user
from app.services.weather_fetcher import geocode_city, fetch_current_weather, fetch_forecast
from app.services.forecast_engine import (
    generate_alerts, generate_forecast_alerts, compute_statistics,
)

router = APIRouter(prefix="/weather", tags=["Weather"])


def _save_record(db: Session, data: dict):
    """Persist a current-weather fetch to the history table."""
    record = WeatherRecord(**{
        k: v for k, v in data.items()
        if k not in ("city_name", "country_code", "latitude", "longitude", "fetched_at")
    })
    record.city_name = data["city_name"]
    record.country_code = data["country_code"]
    record.latitude = data["latitude"]
    record.longitude = data["longitude"]
    record.fetched_at = data["fetched_at"]
    db.add(record)
    db.commit()


# ── Current weather ────────────────────────────────────────────────────────────

@router.get("/current", response_model=CurrentWeather)
async def get_current(
    city: str = Query(..., description="City name, e.g. 'Vilnius'"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    lat, lon, name, country = await geocode_city(city)
    data = await fetch_current_weather(lat, lon, name, country)
    _save_record(db, data)
    return CurrentWeather(**data)


# ── 7-day forecast ─────────────────────────────────────────────────────────────

@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    city: str = Query(..., description="City name"),
    days: int = Query(7, ge=1, le=16, description="Number of forecast days (1–16)"),
    _: User = Depends(get_current_user),
):
    lat, lon, name, country = await geocode_city(city)
    data = await fetch_forecast(lat, lon, name, country, days)
    return ForecastResponse(**data)


# ── Weather alerts (current + forecast) ───────────────────────────────────────

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    city: str = Query(..., description="City name"),
    include_forecast: bool = Query(True, description="Also check upcoming forecast days"),
    _: User = Depends(get_current_user),
):
    lat, lon, name, country = await geocode_city(city)
    current_data = await fetch_current_weather(lat, lon, name, country)
    alerts = generate_alerts(current_data)

    if include_forecast:
        forecast_data = await fetch_forecast(lat, lon, name, country, days=7)
        alerts += generate_forecast_alerts(forecast_data["days"])

    return AlertsResponse(
        city_name=name,
        country_code=country,
        alerts=alerts,
        checked_at=datetime.now(timezone.utc),
    )


# ── Historical data & statistics ───────────────────────────────────────────────

@router.get("/history", response_model=List[CurrentWeather])
def get_history(
    city: str = Query(..., description="City name"),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    records = (
        db.query(WeatherRecord)
        .filter(WeatherRecord.city_name.ilike(f"%{city}%"))
        .order_by(WeatherRecord.fetched_at.desc())
        .limit(limit)
        .all()
    )
    return [
        CurrentWeather(
            city_name=r.city_name,
            country_code=r.country_code,
            latitude=r.latitude,
            longitude=r.longitude,
            temperature=r.temperature or 0,
            apparent_temperature=r.apparent_temperature or 0,
            humidity=r.humidity or 0,
            wind_speed=r.wind_speed or 0,
            wind_direction=r.wind_direction or 0,
            precipitation=r.precipitation or 0,
            snowfall=r.snowfall or 0,
            cloud_cover=r.cloud_cover or 0,
            pressure=r.pressure or 0,
            weather_code=r.weather_code or 0,
            weather_description=r.weather_description or "",
            is_day=r.is_day or 1,
            fetched_at=r.fetched_at,
        )
        for r in records
    ]


@router.get("/analysis", response_model=StatsSummary)
def get_analysis(
    city: str = Query(..., description="City name"),
    days: int = Query(7, ge=1, le=90, description="Look-back period in days"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stats = compute_statistics(db, city, days)
    return StatsSummary(**stats)


# ── Multi-city comparison ──────────────────────────────────────────────────────

@router.get("/compare", response_model=CompareResponse)
async def compare_cities(
    cities: str = Query(..., description="Comma-separated city names, e.g. 'Vilnius,Warsaw,Riga'"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    city_list = [c.strip() for c in cities.split(",") if c.strip()]
    if len(city_list) < 2:
        from fastapi import HTTPException
        raise HTTPException(400, "Provide at least 2 cities to compare")
    if len(city_list) > 10:
        from fastapi import HTTPException
        raise HTTPException(400, "Maximum 10 cities per comparison")

    results: List[CityCompareItem] = []
    for city in city_list:
        lat, lon, name, country = await geocode_city(city)
        data = await fetch_current_weather(lat, lon, name, country)
        _save_record(db, data)
        results.append(CityCompareItem(
            city_name=data["city_name"],
            country_code=data["country_code"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            temperature=data["temperature"],
            apparent_temperature=data["apparent_temperature"],
            humidity=data["humidity"],
            wind_speed=data["wind_speed"],
            precipitation=data["precipitation"],
            weather_description=data["weather_description"],
        ))

    warmest = max(results, key=lambda x: x.temperature).city_name
    coldest = min(results, key=lambda x: x.temperature).city_name
    most_humid = max(results, key=lambda x: x.humidity).city_name
    windiest = max(results, key=lambda x: x.wind_speed).city_name

    return CompareResponse(
        cities=results,
        compared_at=datetime.now(timezone.utc),
        warmest=warmest,
        coldest=coldest,
        most_humid=most_humid,
        windiest=windiest,
    )
