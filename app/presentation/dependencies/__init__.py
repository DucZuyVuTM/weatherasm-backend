from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.infrastructure.repositories import SqlUserRepository
from app.infrastructure.external.open_meteo import OpenMeteoGateway
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError
from app.domain.entities import UserEntity
from app.core.config import DEBUG

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_weather_gateway() -> OpenMeteoGateway:
    # verify=False only in local dev; production Linux env doesn't need this
    return OpenMeteoGateway(verify_ssl=not DEBUG)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserEntity:
    try:
        payload = decode_token(token)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    repo = SqlUserRepository(db)
    user = repo.find_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_current_admin(current_user: UserEntity = Depends(get_current_user)) -> UserEntity:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
