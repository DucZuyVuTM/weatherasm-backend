import statistics
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import (
    ALERT_WIND_SPEED_KMH, ALERT_PRECIPITATION_MM,
    ALERT_TEMP_HIGH_C, ALERT_TEMP_LOW_C, ALERT_SNOWFALL_CM,
)
from app.models.location import Location
from app.models.weather_record import WeatherRecord
from app.schemas.weather import WeatherAlert


def generate_alerts(weather: dict) -> List[WeatherAlert]:
    """Analyze current weather data and produce a list of alerts."""
    alerts = []

    wind = weather.get("wind_speed") or 0
    if wind >= ALERT_WIND_SPEED_KMH:
        level = "warning" if wind >= 90 else "watch"
        alerts.append(WeatherAlert(
            level=level, type="wind",
            message=f"Strong wind expected: {wind:.1f} km/h",
            value=wind, threshold=ALERT_WIND_SPEED_KMH, unit="km/h",
        ))

    rain = weather.get("precipitation") or 0
    if rain >= ALERT_PRECIPITATION_MM:
        level = "warning" if rain >= 40 else "watch"
        alerts.append(WeatherAlert(
            level=level, type="rain",
            message=f"Heavy precipitation: {rain:.1f} mm",
            value=rain, threshold=ALERT_PRECIPITATION_MM, unit="mm",
        ))

    snow = weather.get("snowfall") or 0
    if snow >= ALERT_SNOWFALL_CM:
        alerts.append(WeatherAlert(
            level="watch", type="snow",
            message=f"Heavy snowfall: {snow:.1f} cm",
            value=snow, threshold=ALERT_SNOWFALL_CM, unit="cm",
        ))

    temp = weather.get("temperature")
    if temp is not None:
        if temp >= ALERT_TEMP_HIGH_C:
            alerts.append(WeatherAlert(
                level="warning", type="heat",
                message=f"Extreme heat: {temp:.1f}°C",
                value=temp, threshold=ALERT_TEMP_HIGH_C, unit="°C",
            ))
        elif temp <= ALERT_TEMP_LOW_C:
            alerts.append(WeatherAlert(
                level="warning", type="cold",
                message=f"Extreme cold: {temp:.1f}°C",
                value=temp, threshold=ALERT_TEMP_LOW_C, unit="°C",
            ))

    # Thunderstorm codes: 95, 96, 99
    if weather.get("weather_code") in (95, 96, 99):
        alerts.append(WeatherAlert(
            level="warning", type="thunderstorm",
            message="Thunderstorm in progress",
            value=weather["weather_code"], threshold=95, unit="WMO code",
        ))

    return alerts


def generate_forecast_alerts(forecast_days: List[dict]) -> List[WeatherAlert]:
    """Check upcoming forecast days for alert conditions."""
    alerts = []
    for day in forecast_days:
        date_str = str(day.get("forecast_date", ""))

        wind = day.get("wind_speed_max") or 0
        if wind >= ALERT_WIND_SPEED_KMH:
            alerts.append(WeatherAlert(
                level="watch", type="wind",
                message=f"Strong wind forecasted on {date_str}: {wind:.1f} km/h",
                value=wind, threshold=ALERT_WIND_SPEED_KMH, unit="km/h",
            ))

        rain = day.get("precipitation_sum") or 0
        if rain >= ALERT_PRECIPITATION_MM:
            alerts.append(WeatherAlert(
                level="watch", type="rain",
                message=f"Heavy rain forecasted on {date_str}: {rain:.1f} mm",
                value=rain, threshold=ALERT_PRECIPITATION_MM, unit="mm",
            ))

        snow = day.get("snowfall_sum") or 0
        if snow >= ALERT_SNOWFALL_CM:
            alerts.append(WeatherAlert(
                level="advisory", type="snow",
                message=f"Snowfall forecasted on {date_str}: {snow:.1f} cm",
                value=snow, threshold=ALERT_SNOWFALL_CM, unit="cm",
            ))

        t_max = day.get("temp_max")
        t_min = day.get("temp_min")
        if t_max is not None and t_max >= ALERT_TEMP_HIGH_C:
            alerts.append(WeatherAlert(
                level="watch", type="heat",
                message=f"Extreme heat on {date_str}: {t_max:.1f}°C",
                value=t_max, threshold=ALERT_TEMP_HIGH_C, unit="°C",
            ))
        if t_min is not None and t_min <= ALERT_TEMP_LOW_C:
            alerts.append(WeatherAlert(
                level="watch", type="cold",
                message=f"Extreme cold on {date_str}: {t_min:.1f}°C",
                value=t_min, threshold=ALERT_TEMP_LOW_C, unit="°C",
            ))

    return alerts


def compute_statistics(db: Session, city_name: str, period_days: int) -> dict:
    """Compute stats from historical WeatherRecord rows for a city."""
    since = datetime.now(timezone.utc) - timedelta(days=period_days)
    records: List[WeatherRecord] = (
        db.query(WeatherRecord)
        .join(Location, WeatherRecord.location_id == Location.id)
        .filter(
            Location.city_name.ilike(f"%{city_name}%"),
            WeatherRecord.fetched_at >= since,
        )
        .order_by(WeatherRecord.fetched_at)
        .all()
    )

    if not records:
        return {
            "city_name": city_name,
            "country_code": None,
            "period_days": period_days,
            "temp_avg": None, "temp_max": None, "temp_min": None, "temp_std": None,
            "humidity_avg": None, "wind_speed_avg": None, "wind_speed_max": None,
            "precipitation_total": None, "most_common_condition": None,
            "records_count": 0,
        }

    location = db.query(Location).filter(Location.id == records[0].location_id).first()

    temps = [r.temperature for r in records if r.temperature is not None]
    humidities = [r.humidity for r in records if r.humidity is not None]
    winds = [r.wind_speed for r in records if r.wind_speed is not None]
    precips = [r.precipitation for r in records if r.precipitation is not None]
    conditions = [r.weather_description for r in records if r.weather_description]

    most_common = None
    if conditions:
        most_common = max(set(conditions), key=conditions.count)

    return {
        "city_name": location.city_name if location else city_name,
        "country_code": location.country_code if location else None,
        "period_days": period_days,
        "temp_avg": round(statistics.mean(temps), 2) if temps else None,
        "temp_max": round(max(temps), 2) if temps else None,
        "temp_min": round(min(temps), 2) if temps else None,
        "temp_std": round(statistics.stdev(temps), 2) if len(temps) > 1 else None,
        "humidity_avg": round(statistics.mean(humidities), 2) if humidities else None,
        "wind_speed_avg": round(statistics.mean(winds), 2) if winds else None,
        "wind_speed_max": round(max(winds), 2) if winds else None,
        "precipitation_total": round(sum(precips), 2) if precips else None,
        "most_common_condition": most_common,
        "records_count": len(records),
    }
