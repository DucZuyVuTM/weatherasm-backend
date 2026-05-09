from datetime import datetime, timezone
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
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
