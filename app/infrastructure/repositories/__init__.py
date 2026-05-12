import statistics as stats_lib
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities import (
    UserEntity, LocationEntity, SavedLocationEntity,
    WeatherRecordEntity, WeatherStatsEntity,
)
from app.domain.repositories import (
    IUserRepository, ILocationRepository,
    ISavedLocationRepository, IWeatherRecordRepository,
)
from app.infrastructure.database.models import (
    UserORM, LocationORM, SavedLocationORM, WeatherRecordORM,
)


def _user_to_entity(orm: UserORM) -> UserEntity:
    return UserEntity(
        id=orm.id, email=orm.email, username=orm.username,
        hashed_password=orm.hashed_password, full_name=orm.full_name,
        role=orm.role, is_active=orm.is_active,
        created_at=orm.created_at, updated_at=orm.updated_at,
    )


def _location_to_entity(orm: LocationORM) -> LocationEntity:
    return LocationEntity(
        id=orm.id, city_name=orm.city_name,
        country_code=orm.country_code,
        latitude=orm.latitude, longitude=orm.longitude,
    )


def _record_to_entity(orm: WeatherRecordORM, loc: Optional[LocationEntity] = None) -> WeatherRecordEntity:
    return WeatherRecordEntity(
        id=orm.id, location_id=orm.location_id,
        temperature=orm.temperature, apparent_temperature=orm.apparent_temperature,
        humidity=orm.humidity, wind_speed=orm.wind_speed,
        wind_direction=orm.wind_direction, precipitation=orm.precipitation,
        snowfall=orm.snowfall, cloud_cover=orm.cloud_cover,
        pressure=orm.pressure, weather_code=orm.weather_code,
        weather_description=orm.weather_description,
        is_day=orm.is_day, fetched_at=orm.fetched_at,
        location=loc,
    )


class SqlUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self._db = db

    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        orm = self._db.query(UserORM).filter(UserORM.id == user_id).first()
        return _user_to_entity(orm) if orm else None

    def find_by_email(self, email: str) -> Optional[UserEntity]:
        orm = self._db.query(UserORM).filter(UserORM.email == email).first()
        return _user_to_entity(orm) if orm else None

    def find_by_username(self, username: str) -> Optional[UserEntity]:
        orm = self._db.query(UserORM).filter(UserORM.username == username).first()
        return _user_to_entity(orm) if orm else None

    def find_all(self, skip: int, limit: int) -> List[UserEntity]:
        return [_user_to_entity(u) for u in self._db.query(UserORM).offset(skip).limit(limit).all()]

    def save(self, user: UserEntity) -> UserEntity:
        if user.id:
            orm = self._db.query(UserORM).filter(UserORM.id == user.id).first()
            orm.email = user.email
            orm.full_name = user.full_name
            orm.hashed_password = user.hashed_password
            orm.is_active = user.is_active
        else:
            orm = UserORM(
                email=user.email, username=user.username,
                hashed_password=user.hashed_password, full_name=user.full_name,
            )
            self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        return _user_to_entity(orm)

    def delete(self, user_id: int) -> None:
        self._db.query(UserORM).filter(UserORM.id == user_id).delete()
        self._db.commit()


class SqlLocationRepository(ILocationRepository):
    def __init__(self, db: Session):
        self._db = db

    def find_by_coords(self, lat: float, lon: float) -> Optional[LocationEntity]:
        orm = self._db.query(LocationORM).filter(
            LocationORM.latitude == lat, LocationORM.longitude == lon
        ).first()
        return _location_to_entity(orm) if orm else None

    def save(self, location: LocationEntity) -> LocationEntity:
        orm = LocationORM(
            city_name=location.city_name, country_code=location.country_code,
            latitude=location.latitude, longitude=location.longitude,
        )
        self._db.add(orm)
        self._db.flush()
        return _location_to_entity(orm)


class SqlSavedLocationRepository(ISavedLocationRepository):
    def __init__(self, db: Session):
        self._db = db

    def find_by_user(self, user_id: int) -> List[SavedLocationEntity]:
        rows = (
            self._db.query(SavedLocationORM, LocationORM)
            .join(LocationORM, SavedLocationORM.location_id == LocationORM.id)
            .filter(SavedLocationORM.user_id == user_id)
            .all()
        )
        return [
            SavedLocationEntity(
                id=s.id, user_id=s.user_id, location_id=s.location_id,
                location=_location_to_entity(loc), created_at=s.created_at,
            )
            for s, loc in rows
        ]

    def find_by_user_and_location(self, user_id: int, location_id: int) -> Optional[SavedLocationEntity]:
        orm = self._db.query(SavedLocationORM).filter(
            SavedLocationORM.user_id == user_id,
            SavedLocationORM.location_id == location_id,
        ).first()
        return SavedLocationEntity(id=orm.id, user_id=orm.user_id, location_id=orm.location_id) if orm else None

    def find_by_id_and_user(self, saved_id: int, user_id: int) -> Optional[SavedLocationEntity]:
        orm = self._db.query(SavedLocationORM).filter(
            SavedLocationORM.id == saved_id,
            SavedLocationORM.user_id == user_id,
        ).first()
        return SavedLocationEntity(id=orm.id, user_id=orm.user_id, location_id=orm.location_id) if orm else None

    def save(self, saved: SavedLocationEntity) -> SavedLocationEntity:
        orm = SavedLocationORM(user_id=saved.user_id, location_id=saved.location_id)
        self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        saved.id = orm.id
        saved.created_at = orm.created_at
        return saved

    def delete(self, saved_id: int) -> None:
        self._db.query(SavedLocationORM).filter(SavedLocationORM.id == saved_id).delete()
        self._db.commit()


class SqlWeatherRecordRepository(IWeatherRecordRepository):
    def __init__(self, db: Session):
        self._db = db

    def save(self, record: WeatherRecordEntity) -> WeatherRecordEntity:
        orm = WeatherRecordORM(
            location_id=record.location_id,
            temperature=record.temperature, apparent_temperature=record.apparent_temperature,
            humidity=record.humidity, wind_speed=record.wind_speed,
            wind_direction=record.wind_direction, precipitation=record.precipitation,
            snowfall=record.snowfall, cloud_cover=record.cloud_cover,
            pressure=record.pressure, weather_code=record.weather_code,
            weather_description=record.weather_description,
            is_day=record.is_day, fetched_at=record.fetched_at,
        )
        self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        record.id = orm.id
        return record

    def find_by_city(self, city_name: str, limit: int) -> List[WeatherRecordEntity]:
        rows = (
            self._db.query(WeatherRecordORM, LocationORM)
            .join(LocationORM, WeatherRecordORM.location_id == LocationORM.id)
            .filter(LocationORM.city_name.ilike(f"%{city_name}%"))
            .order_by(WeatherRecordORM.fetched_at.desc())
            .limit(limit)
            .all()
        )
        return [_record_to_entity(rec, _location_to_entity(loc)) for rec, loc in rows]

    def compute_stats(self, city_name: str, period_days: int) -> WeatherStatsEntity:
        since = datetime.now(timezone.utc) - timedelta(days=period_days)
        rows = (
            self._db.query(WeatherRecordORM, LocationORM)
            .join(LocationORM, WeatherRecordORM.location_id == LocationORM.id)
            .filter(
                LocationORM.city_name.ilike(f"%{city_name}%"),
                WeatherRecordORM.fetched_at >= since,
            )
            .order_by(WeatherRecordORM.fetched_at)
            .all()
        )
        if not rows:
            return WeatherStatsEntity(
                city_name=city_name, country_code=None, period_days=period_days,
                temp_avg=None, temp_max=None, temp_min=None, temp_std=None,
                humidity_avg=None, wind_speed_avg=None, wind_speed_max=None,
                precipitation_total=None, most_common_condition=None, records_count=0,
            )

        records = [r for r, _ in rows]
        loc = rows[0][1]
        temps = [r.temperature for r in records if r.temperature is not None]
        humidities = [r.humidity for r in records if r.humidity is not None]
        winds = [r.wind_speed for r in records if r.wind_speed is not None]
        precips = [r.precipitation for r in records if r.precipitation is not None]
        conditions = [r.weather_description for r in records if r.weather_description]

        return WeatherStatsEntity(
            city_name=loc.city_name, country_code=loc.country_code,
            period_days=period_days,
            temp_avg=round(stats_lib.mean(temps), 2) if temps else None,
            temp_max=round(max(temps), 2) if temps else None,
            temp_min=round(min(temps), 2) if temps else None,
            temp_std=round(stats_lib.stdev(temps), 2) if len(temps) > 1 else None,
            humidity_avg=round(stats_lib.mean(humidities), 2) if humidities else None,
            wind_speed_avg=round(stats_lib.mean(winds), 2) if winds else None,
            wind_speed_max=round(max(winds), 2) if winds else None,
            precipitation_total=round(sum(precips), 2) if precips else None,
            most_common_condition=max(set(conditions), key=conditions.count) if conditions else None,
            records_count=len(records),
        )
