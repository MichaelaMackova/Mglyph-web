from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
import errors as mglyph_errors
from db.database import SessionDep
from db.models.userModel import UserModel, UserRole


from api.auth.utils import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY, validate_jwt_token


bearer_scheme = HTTPBearer(auto_error=False)

def get_jwt_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        err = mglyph_errors.UnauthorizedError("Missing authorization token or invalid scheme", mglyph_errors.ErrorCode.UNAUTHORIZED_MISSING_TOKEN)
        raise mglyph_errors.UnauthorizedError.HTTPException(err, headers={"WWW-Authenticate": "Bearer"})
    return credentials.credentials

def validate_access_token(token: str = Depends(get_jwt_token)) -> str:
    return validate_jwt_token(token, JWT_ACCESS_SECRET_KEY)

def validate_refresh_token(token: str = Depends(get_jwt_token)) -> str:
    return validate_jwt_token(token, JWT_REFRESH_SECRET_KEY)


CurrentUserIdDep = Annotated[str, Depends(validate_access_token)]


async def validate_user_is_admin(user_id: CurrentUserIdDep, session: SessionDep) -> str:
    db_user = await session.get(UserModel, user_id)
    if not db_user:
        err = mglyph_errors.UnauthorizedError("Logged in user", mglyph_errors.ErrorCode.UNAUTHORIZED_USER_NOT_FOUND)
        raise mglyph_errors.UnauthorizedError.HTTPException(err)
    if db_user.role != UserRole.admin:
        err = mglyph_errors.ForbiddenError("Admin privileges required", mglyph_errors.ErrorCode.FORBIDDEN_NOT_ADMIN)
        raise mglyph_errors.ForbiddenError.HTTPException(err)
    return user_id


CurrentAdminUserIdDep = Annotated[str, Depends(validate_user_is_admin)]
