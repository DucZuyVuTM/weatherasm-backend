from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.database import Base


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, nullable=False, index=True)
    country_code = Column(String(2), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)          # °C
    apparent_temperature = Column(Float, nullable=True) # feels like °C
    humidity = Column(Float, nullable=True)             # %
    wind_speed = Column(Float, nullable=True)           # km/h
    wind_direction = Column(Float, nullable=True)       # degrees
    precipitation = Column(Float, nullable=True)        # mm
    snowfall = Column(Float, nullable=True)             # cm
    cloud_cover = Column(Float, nullable=True)          # %
    pressure = Column(Float, nullable=True)             # hPa
    weather_code = Column(Integer, nullable=True)       # WMO weather code
    weather_description = Column(String, nullable=True)
    is_day = Column(Integer, nullable=True)             # 1=day, 0=night
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
