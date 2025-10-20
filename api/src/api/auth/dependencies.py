from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


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
