from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.infrastructure.repositories import SqlUserRepository
from app.application.dto import UserCreateDTO, UserResponseDTO, TokenResponseDTO, RefreshRequestDTO
from app.application.mappers import user_to_dto
from app.domain.use_cases import RegisterUserUseCase, LoginUserUseCase
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.core.exceptions import ConflictError, UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreateDTO, db: Session = Depends(get_db)):
    use_case = RegisterUserUseCase(SqlUserRepository(db))
    user = use_case.execute(payload.email, payload.username, payload.password, payload.full_name)
    return user_to_dto(user)


@router.post("/login", response_model=TokenResponseDTO)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    use_case = LoginUserUseCase(SqlUserRepository(db))
    tokens = use_case.execute(form.username, form.password)
    return TokenResponseDTO(**tokens)


@router.post("/refresh", response_model=TokenResponseDTO)
def refresh_token(payload: RefreshRequestDTO, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(payload.refresh_token)
    except UnauthorizedError as e:
        raise HTTPException(401, str(e))
    if token_data.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    user = SqlUserRepository(db).find_by_id(int(token_data["sub"]))
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    return TokenResponseDTO(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )
