from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ValidationError
from jose import jwt
from fastapi import HTTPException, status
import errors as mglyph_errors

from settings import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_MINUTES

ALGORITHM = "HS256" # TODO: .env?

class TokenPayload(BaseModel):
    exp: datetime
    user_id: str


def create_jwt_token(user_id: str, jwt_secret_key: str, expires_delta: timedelta) -> str:
    expires_timestamp = datetime.now(timezone.utc) + expires_delta
    to_encode = TokenPayload(exp=expires_timestamp, user_id=user_id).model_dump() # {"exp": expires_timestamp, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, ALGORITHM)
    return encoded_jwt

def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(user_id, JWT_ACCESS_SECRET_KEY, expires_delta)

def create_refresh_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(user_id, JWT_REFRESH_SECRET_KEY, expires_delta)



def validate_jwt_token(token: str, secret_key: str) -> str:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM], options={"verify_exp": False})
        token_data = TokenPayload(**payload)

        if token_data.exp < datetime.now(timezone.utc):
            err = mglyph_errors.UnauthorizedError("Token expired", mglyph_errors.ErrorCode.UNAUTHORIZED_EXPIRED_TOKEN)
            raise mglyph_errors.UnauthorizedError.HTTPException(err, headers={"WWW-Authenticate": "Bearer"})
    except (jwt.JWTError, ValidationError):
        err = mglyph_errors.UnauthorizedError("Could not validate credentials", mglyph_errors.ErrorCode.UNAUTHORIZED_INVALID_TOKEN)
        raise mglyph_errors.UnauthorizedError.HTTPException(err, headers={"WWW-Authenticate": "Bearer"})
    return token_data.user_id
