from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, nullable=False, index=True)
    country_code = Column(String(2), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    forecast_date = Column(Date, nullable=False)
    temp_max = Column(Float, nullable=True)           # °C
    temp_min = Column(Float, nullable=True)           # °C
    precipitation_sum = Column(Float, nullable=True)  # mm
    snowfall_sum = Column(Float, nullable=True)       # cm
    wind_speed_max = Column(Float, nullable=True)     # km/h
    wind_gusts_max = Column(Float, nullable=True)     # km/h
    weather_code = Column(Integer, nullable=True)
    weather_description = Column(String, nullable=True)
    sunrise = Column(String, nullable=True)
    sunset = Column(String, nullable=True)
    uv_index_max = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
