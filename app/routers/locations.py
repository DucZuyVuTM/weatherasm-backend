from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.location import Location, SavedLocation
from app.schemas.location import LocationCreate, LocationResponse
from app.core.security import get_current_user
from app.services.weather_fetcher import geocode_city

router = APIRouter(prefix="/locations", tags=["Saved Locations"])


@router.get("/", response_model=List[LocationResponse])
def get_my_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = (
        db.query(SavedLocation, Location)
        .join(Location, SavedLocation.location_id == Location.id)
        .filter(SavedLocation.user_id == current_user.id)
        .all()
    )
    return [
        LocationResponse(
            id=saved.id,
            city_name=loc.city_name,
            country_code=loc.country_code,
            latitude=loc.latitude,
            longitude=loc.longitude,
            created_at=saved.created_at,
        )
        for saved, loc in results
    ]


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def add_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lat, lon, resolved_name, country_code = await geocode_city(payload.city_name)

    loc = db.query(Location).filter(
        Location.latitude == lat,
        Location.longitude == lon,
    ).first()

    if not loc:
        loc = Location(
            city_name=resolved_name,
            country_code=country_code,
            latitude=lat,
            longitude=lon,
        )
        db.add(loc)
        db.flush()  # lấy loc.id

    existing = db.query(SavedLocation).filter(
        SavedLocation.user_id == current_user.id,
        SavedLocation.location_id == loc.id
    ).first()
    if existing:
        raise HTTPException(400, f"Location '{resolved_name}' already saved")

    saved = SavedLocation(
        user_id=current_user.id,
        location_id=loc.id,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)

    return LocationResponse(
        id=saved.id,
        city_name=loc.city_name,
        country_code=loc.country_code,
        latitude=loc.latitude,
        longitude=loc.longitude,
        created_at=saved.created_at,
    )


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
