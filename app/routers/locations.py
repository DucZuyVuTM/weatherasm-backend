from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.location import SavedLocation
from app.schemas.location import LocationCreate, LocationResponse
from app.core.security import get_current_user
from app.services.weather_fetcher import geocode_city

router = APIRouter(prefix="/locations", tags=["Saved Locations"])


@router.get("/", response_model=List[LocationResponse])
def get_my_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(SavedLocation).filter(SavedLocation.user_id == current_user.id).all()


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def add_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lat, lon, resolved_name, country_code = await geocode_city(payload.city_name)

    existing = db.query(SavedLocation).filter(
        SavedLocation.user_id == current_user.id,
        SavedLocation.latitude == lat,
        SavedLocation.longitude == lon,
    ).first()
    if existing:
        raise HTTPException(400, f"Location '{resolved_name}' already saved")

    loc = SavedLocation(
        user_id=current_user.id,
        city_name=resolved_name,
        country_code=country_code,
        latitude=lat,
        longitude=lon,
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loc = db.query(SavedLocation).filter(
        SavedLocation.id == location_id,
        SavedLocation.user_id == current_user.id,
    ).first()
    if not loc:
        raise HTTPException(404, "Location not found")
    db.delete(loc)
    db.commit()
