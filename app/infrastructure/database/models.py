from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float,
    ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum("user", "admin", name="user_role"), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class LocationORM(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    city_name = Column(String, nullable=False)
    country_code = Column(String(2), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("latitude", "longitude", name="uq_location_coords"),)


class SavedLocationORM(Base):
    __tablename__ = "saved_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("user_id", "location_id", name="uq_user_location"),)


class WeatherRecordORM(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    temperature = Column(Float, nullable=True)
    apparent_temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    snowfall = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    weather_description = Column(String, nullable=True)
    is_day = Column(Integer, nullable=True)
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ForecastORM(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    forecast_date = Column(Date, nullable=False)
    temp_max = Column(Float, nullable=True)
    temp_min = Column(Float, nullable=True)
    precipitation_sum = Column(Float, nullable=True)
    snowfall_sum = Column(Float, nullable=True)
    wind_speed_max = Column(Float, nullable=True)
    wind_gusts_max = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    weather_description = Column(String, nullable=True)
    sunrise = Column(String, nullable=True)
    sunset = Column(String, nullable=True)
    uv_index_max = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
