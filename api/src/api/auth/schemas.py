from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from db.models.userModel import UserModel

class TokenPayload(BaseModel):
    exp: datetime
    user_id: str


class CredentialDTO(BaseModel):
    credential: str

class UserPublicDTO(BaseModel):
    id: UUID
    email: str
    count: int

    @staticmethod
    def from_model(userModel: UserModel) -> "UserPublicDTO":
        return UserPublicDTO(id=userModel.id, email=userModel.email, count=userModel.count)

class LoggedInUserDTO(BaseModel):
    access_token: str
    refresh_token: str
    user_info: UserPublicDTO