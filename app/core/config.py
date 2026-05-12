import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/weatherdb")
SECRET_KEY: str = os.getenv("SECRET_KEY", "changethis-secret-key")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
APP_NAME: str = os.getenv("APP_NAME", "WeatherAnalysis API")
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
PRODUCTION_ORIGIN: str = os.getenv("PRODUCTION_ORIGIN", "http://localhost:5173")

OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
GEOCODING_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1"

ALERT_WIND_SPEED_KMH: float = 60.0
ALERT_PRECIPITATION_MM: float = 20.0
ALERT_TEMP_HIGH_C: float = 35.0
ALERT_TEMP_LOW_C: float = -15.0
ALERT_SNOWFALL_CM: float = 10.0
