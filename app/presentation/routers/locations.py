from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.infrastructure.repositories import SqlLocationRepository, SqlSavedLocationRepository
from app.infrastructure.external.open_meteo import OpenMeteoGateway
from app.application.dto import LocationCreateDTO, LocationResponseDTO
from app.application.mappers import saved_location_to_dto
from app.domain.use_cases import AddSavedLocationUseCase
from app.domain.entities import UserEntity
from app.presentation.dependencies import get_current_user, get_weather_gateway

router = APIRouter(prefix="/locations", tags=["Saved Locations"])


@router.get("/", response_model=List[LocationResponseDTO])
def get_my_locations(
    db: Session = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    saved = SqlSavedLocationRepository(db).find_by_user(current_user.id)
    return [saved_location_to_dto(s) for s in saved]


@router.post("/", response_model=LocationResponseDTO, status_code=status.HTTP_201_CREATED)
async def add_location(
    payload: LocationCreateDTO,
    db: Session = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
    gateway: OpenMeteoGateway = Depends(get_weather_gateway),
):
    use_case = AddSavedLocationUseCase(
        SqlLocationRepository(db),
        SqlSavedLocationRepository(db),
        gateway,
    )
    saved = await use_case.execute(current_user.id, payload.city_name)
    return saved_location_to_dto(saved)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    repo = SqlSavedLocationRepository(db)
    loc = repo.find_by_id_and_user(location_id, current_user.id)
    if not loc:
        raise HTTPException(404, "Location not found")
    repo.delete(location_id)
