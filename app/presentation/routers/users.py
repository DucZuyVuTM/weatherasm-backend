from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.infrastructure.repositories import SqlUserRepository
from app.application.dto import UserResponseDTO, UserUpdateDTO, PasswordChangeDTO
from app.application.mappers import user_to_dto
from app.domain.use_cases import UpdateUserUseCase, ChangePasswordUseCase
from app.domain.entities import UserEntity
from app.presentation.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponseDTO)
def get_me(current_user: UserEntity = Depends(get_current_user)):
    return user_to_dto(current_user)


@router.put("/me", response_model=UserResponseDTO)
def update_me(
    payload: UserUpdateDTO,
    db: Session = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    use_case = UpdateUserUseCase(SqlUserRepository(db))
    updated = use_case.execute(current_user, payload.email, payload.full_name)
    return user_to_dto(updated)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChangeDTO,
    db: Session = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    ChangePasswordUseCase(SqlUserRepository(db)).execute(
        current_user, payload.current_password, payload.new_password
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), current_user: UserEntity = Depends(get_current_user)):
    SqlUserRepository(db).delete(current_user.id)


@router.get("/", response_model=List[UserResponseDTO])
def list_users(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    _: UserEntity = Depends(get_current_admin),
):
    return [user_to_dto(u) for u in SqlUserRepository(db).find_all(skip, limit)]


@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: UserEntity = Depends(get_current_admin),
):
    user = SqlUserRepository(db).find_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user_to_dto(user)


@router.patch("/{user_id}/deactivate", response_model=UserResponseDTO)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: UserEntity = Depends(get_current_admin),
):
    if user_id == current_admin.id:
        raise HTTPException(400, "Cannot deactivate your own account")
    repo = SqlUserRepository(db)
    user = repo.find_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = False
    return user_to_dto(repo.save(user))
