from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LocationCreate(BaseModel):
    city_name: str


class LocationResponse(BaseModel):
    id: int
    city_name: str
    country_code: Optional[str]
    latitude: float
    longitude: float
    created_at: datetime

    model_config = {"from_attributes": True}
