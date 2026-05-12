from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities import (
    UserEntity, LocationEntity, SavedLocationEntity,
    WeatherRecordEntity, ForecastEntity, WeatherStatsEntity,
)


class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[UserEntity]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserEntity]: ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[UserEntity]: ...

    @abstractmethod
    def find_all(self, skip: int, limit: int) -> List[UserEntity]: ...

    @abstractmethod
    def save(self, user: UserEntity) -> UserEntity: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...


class ILocationRepository(ABC):
    @abstractmethod
    def find_by_coords(self, lat: float, lon: float) -> Optional[LocationEntity]: ...

    @abstractmethod
    def save(self, location: LocationEntity) -> LocationEntity: ...


class ISavedLocationRepository(ABC):
    @abstractmethod
    def find_by_user(self, user_id: int) -> List[SavedLocationEntity]: ...

    @abstractmethod
    def find_by_user_and_location(self, user_id: int, location_id: int) -> Optional[SavedLocationEntity]: ...

    @abstractmethod
    def find_by_id_and_user(self, saved_id: int, user_id: int) -> Optional[SavedLocationEntity]: ...

    @abstractmethod
    def save(self, saved: SavedLocationEntity) -> SavedLocationEntity: ...

    @abstractmethod
    def delete(self, saved_id: int) -> None: ...


class IWeatherRecordRepository(ABC):
    @abstractmethod
    def save(self, record: WeatherRecordEntity) -> WeatherRecordEntity: ...

    @abstractmethod
    def find_by_city(self, city_name: str, limit: int) -> List[WeatherRecordEntity]: ...

    @abstractmethod
    def compute_stats(self, city_name: str, period_days: int) -> WeatherStatsEntity: ...


class IWeatherGateway(ABC):
    """External weather data source — Open-Meteo or any other provider."""

    @abstractmethod
    async def geocode(self, city_name: str) -> LocationEntity: ...

    @abstractmethod
    async def get_current(self, location: LocationEntity) -> WeatherRecordEntity: ...

    @abstractmethod
    async def get_forecast(self, location: LocationEntity, days: int) -> ForecastEntity: ...
