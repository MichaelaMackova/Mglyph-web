from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from api.users.schemas import UserPublicSimpleDTO

class TokenPayload(BaseModel):
    exp: datetime
    user_id: str


class CredentialDTO(BaseModel):
    credential: str


class GoogleUserCreateDTO(BaseModel):
    username: str
    credential: CredentialDTO


class LoggedInUserDTO(BaseModel):
    access_token: str
    refresh_token: str
    user_info: UserPublicSimpleDTO