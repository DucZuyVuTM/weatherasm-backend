import statistics as stats_lib
from datetime import datetime, timezone
from typing import List, Optional

from app.domain.entities import (
    UserEntity, LocationEntity, SavedLocationEntity,
    WeatherRecordEntity, ForecastEntity, WeatherAlert, WeatherStatsEntity,
)
from app.domain.repositories import (
    IUserRepository, ILocationRepository, ISavedLocationRepository,
    IWeatherRecordRepository, IWeatherGateway,
)
from app.core.config import (
    ALERT_WIND_SPEED_KMH, ALERT_PRECIPITATION_MM,
    ALERT_TEMP_HIGH_C, ALERT_TEMP_LOW_C, ALERT_SNOWFALL_CM,
)
from app.core.exceptions import (
    NotFoundError, ConflictError, UnauthorizedError,
)
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token


# ── Auth ───────────────────────────────────────────────────────────────────────

class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self._repo = user_repo

    def execute(self, email: str, username: str, password: str, full_name: Optional[str]) -> UserEntity:
        if self._repo.find_by_email(email):
            raise ConflictError("Email already registered")
        if self._repo.find_by_username(username):
            raise ConflictError("Username already taken")
        user = UserEntity(
            id=None, email=email, username=username,
            hashed_password=hash_password(password),
            full_name=full_name, role="user", is_active=True,
        )
        return self._repo.save(user)


class LoginUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self._repo = user_repo

    def execute(self, username: str, password: str) -> dict:
        user = self._repo.find_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect username or password")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        return {
            "access_token": create_access_token({"sub": str(user.id)}),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
        }


# ── User management ────────────────────────────────────────────────────────────

class UpdateUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self._repo = user_repo

    def execute(self, user: UserEntity, email: Optional[str], full_name: Optional[str]) -> UserEntity:
        if email and email != user.email:
            if self._repo.find_by_email(email):
                raise ConflictError("Email already taken")
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        return self._repo.save(user)


class ChangePasswordUseCase:
    def __init__(self, user_repo: IUserRepository):
        self._repo = user_repo

    def execute(self, user: UserEntity, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")
        user.hashed_password = hash_password(new_password)
        self._repo.save(user)


# ── Saved locations ────────────────────────────────────────────────────────────

class AddSavedLocationUseCase:
    def __init__(
        self,
        location_repo: ILocationRepository,
        saved_repo: ISavedLocationRepository,
        gateway: IWeatherGateway,
    ):
        self._loc_repo = location_repo
        self._saved_repo = saved_repo
        self._gateway = gateway

    async def execute(self, user_id: int, city_name: str) -> SavedLocationEntity:
        geo = await self._gateway.geocode(city_name)
        loc = self._loc_repo.find_by_coords(geo.latitude, geo.longitude)
        if not loc:
            loc = self._loc_repo.save(geo)

        if self._saved_repo.find_by_user_and_location(user_id, loc.id):
            raise ConflictError(f"Location '{loc.city_name}' already saved")

        saved = SavedLocationEntity(id=None, user_id=user_id, location_id=loc.id, location=loc)
        return self._saved_repo.save(saved)


# ── Weather ────────────────────────────────────────────────────────────────────

class GetCurrentWeatherUseCase:
    def __init__(
        self,
        location_repo: ILocationRepository,
        record_repo: IWeatherRecordRepository,
        gateway: IWeatherGateway,
    ):
        self._loc_repo = location_repo
        self._rec_repo = record_repo
        self._gateway = gateway

    async def execute(self, city_name: str) -> WeatherRecordEntity:
        geo = await self._gateway.geocode(city_name)
        loc = self._loc_repo.find_by_coords(geo.latitude, geo.longitude)
        if not loc:
            loc = self._loc_repo.save(geo)
        record = await self._gateway.get_current(loc)
        record.location_id = loc.id
        record.location = loc
        return self._rec_repo.save(record)


class GetForecastUseCase:
    def __init__(self, gateway: IWeatherGateway):
        self._gateway = gateway

    async def execute(self, city_name: str, days: int) -> ForecastEntity:
        geo = await self._gateway.geocode(city_name)
        return await self._gateway.get_forecast(geo, days)


class GetAlertsUseCase:
    def __init__(self, gateway: IWeatherGateway):
        self._gateway = gateway

    async def execute(self, city_name: str, include_forecast: bool) -> dict:
        geo = await self._gateway.geocode(city_name)
        current = await self._gateway.get_current(geo)
        alerts = _build_current_alerts(current)

        if include_forecast:
            forecast = await self._gateway.get_forecast(geo, days=7)
            alerts += _build_forecast_alerts(forecast)

        return {
            "city_name": geo.city_name,
            "country_code": geo.country_code,
            "alerts": alerts,
            "checked_at": datetime.now(timezone.utc),
        }


class CompareCitiesUseCase:
    def __init__(
        self,
        location_repo: ILocationRepository,
        record_repo: IWeatherRecordRepository,
        gateway: IWeatherGateway,
    ):
        self._loc_repo = location_repo
        self._rec_repo = record_repo
        self._gateway = gateway

    async def execute(self, city_names: List[str]) -> dict:
        results: List[WeatherRecordEntity] = []
        for name in city_names:
            geo = await self._gateway.geocode(name)
            loc = self._loc_repo.find_by_coords(geo.latitude, geo.longitude)
            if not loc:
                loc = self._loc_repo.save(geo)
            record = await self._gateway.get_current(loc)
            record.location_id = loc.id
            record.location = loc
            self._rec_repo.save(record)
            results.append(record)

        return {
            "cities": results,
            "compared_at": datetime.now(timezone.utc),
            "warmest": max(results, key=lambda r: r.temperature or 0).location.city_name,
            "coldest": min(results, key=lambda r: r.temperature or 0).location.city_name,
            "most_humid": max(results, key=lambda r: r.humidity or 0).location.city_name,
            "windiest": max(results, key=lambda r: r.wind_speed or 0).location.city_name,
        }


# ── Alert helpers (pure functions, no I/O) ─────────────────────────────────────

def _build_current_alerts(weather: WeatherRecordEntity) -> List[WeatherAlert]:
    alerts = []
    wind = weather.wind_speed or 0
    if wind >= ALERT_WIND_SPEED_KMH:
        alerts.append(WeatherAlert(
            level="warning" if wind >= 90 else "watch", type="wind",
            message=f"Strong wind: {wind:.1f} km/h",
            value=wind, threshold=ALERT_WIND_SPEED_KMH, unit="km/h",
        ))
    rain = weather.precipitation or 0
    if rain >= ALERT_PRECIPITATION_MM:
        alerts.append(WeatherAlert(
            level="warning" if rain >= 40 else "watch", type="rain",
            message=f"Heavy precipitation: {rain:.1f} mm",
            value=rain, threshold=ALERT_PRECIPITATION_MM, unit="mm",
        ))
    snow = weather.snowfall or 0
    if snow >= ALERT_SNOWFALL_CM:
        alerts.append(WeatherAlert(
            level="watch", type="snow",
            message=f"Heavy snowfall: {snow:.1f} cm",
            value=snow, threshold=ALERT_SNOWFALL_CM, unit="cm",
        ))
    temp = weather.temperature
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
    if weather.weather_code in (95, 96, 99):
        alerts.append(WeatherAlert(
            level="warning", type="thunderstorm",
            message="Thunderstorm in progress",
            value=weather.weather_code, threshold=95, unit="WMO code",
        ))
    return alerts


def _build_forecast_alerts(forecast: ForecastEntity) -> List[WeatherAlert]:
    alerts = []
    for day in forecast.days:
        date_str = str(day.forecast_date)
        wind = day.wind_speed_max or 0
        if wind >= ALERT_WIND_SPEED_KMH:
            alerts.append(WeatherAlert(
                level="watch", type="wind",
                message=f"Strong wind on {date_str}: {wind:.1f} km/h",
                value=wind, threshold=ALERT_WIND_SPEED_KMH, unit="km/h",
            ))
        rain = day.precipitation_sum or 0
        if rain >= ALERT_PRECIPITATION_MM:
            alerts.append(WeatherAlert(
                level="watch", type="rain",
                message=f"Heavy rain on {date_str}: {rain:.1f} mm",
                value=rain, threshold=ALERT_PRECIPITATION_MM, unit="mm",
            ))
        snow = day.snowfall_sum or 0
        if snow >= ALERT_SNOWFALL_CM:
            alerts.append(WeatherAlert(
                level="advisory", type="snow",
                message=f"Snowfall on {date_str}: {snow:.1f} cm",
                value=snow, threshold=ALERT_SNOWFALL_CM, unit="cm",
            ))
        if day.temp_max is not None and day.temp_max >= ALERT_TEMP_HIGH_C:
            alerts.append(WeatherAlert(
                level="watch", type="heat",
                message=f"Extreme heat on {date_str}: {day.temp_max:.1f}°C",
                value=day.temp_max, threshold=ALERT_TEMP_HIGH_C, unit="°C",
            ))
        if day.temp_min is not None and day.temp_min <= ALERT_TEMP_LOW_C:
            alerts.append(WeatherAlert(
                level="watch", type="cold",
                message=f"Extreme cold on {date_str}: {day.temp_min:.1f}°C",
                value=day.temp_min, threshold=ALERT_TEMP_LOW_C, unit="°C",
            ))
    return alerts
