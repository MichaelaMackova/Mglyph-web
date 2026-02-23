from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from db.database import SessionDep
from db.models.userModel import UserModel


from api.auth.utils import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY, validate_jwt_token


bearer_scheme = HTTPBearer()

def get_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    return credentials.credentials

def validate_access_token(token: str = Depends(get_jwt_token)) -> str:
    return validate_jwt_token(token, JWT_ACCESS_SECRET_KEY)

def validate_refresh_token(token: str = Depends(get_jwt_token)) -> str:
    return validate_jwt_token(token, JWT_REFRESH_SECRET_KEY)


CurrentUserIdDep = Annotated[str, Depends(validate_access_token)]


async def validate_user_is_admin(user_id: CurrentUserIdDep, session: SessionDep) -> str:
    db_user = await session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.role != "admin":
        raise HTTPException(status_code=403, detail="User does not have admin privileges")
    return user_id


CurrentAdminUserIdDep = Annotated[str, Depends(validate_user_is_admin)]
