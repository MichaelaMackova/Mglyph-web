from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from api.auth.utils import create_access_token, create_refresh_token

from api.users.schemas import UserPublicSimpleDTO


class CredentialDTO(BaseModel):
    credential: str


class GoogleUserCreateDTO(BaseModel):
    username: str
    credential: CredentialDTO


class LoggedInUserDTO(BaseModel):
    access_token: str
    refresh_token: str
    user_info: UserPublicSimpleDTO

    @staticmethod
    def init_with_new_tokens(user_info: UserPublicSimpleDTO) -> "LoggedInUserDTO":
        return LoggedInUserDTO(
            access_token=create_access_token(user_id=str(user_info.id)),
            refresh_token=create_refresh_token(user_id=str(user_info.id)),
            user_info=user_info
        )