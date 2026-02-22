from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from db.models.userModel import UserModel

class TokenPayload(BaseModel):
    exp: datetime
    user_id: str


class CredentialDTO(BaseModel):
    credential: str



class UserBase(BaseModel):
    username: str
    email: str

class UserPublicSimpleDTO(UserBase):
    id: UUID

    @staticmethod
    def from_model(userModel: UserModel) -> "UserPublicSimpleDTO":
        return UserPublicSimpleDTO(
            id=userModel.id,
            username=userModel.username,
            email=userModel.email
        )

class UserPublicDTO(UserBase):
    id: UUID
    role: str
    count: int #TODO: remove this field, it's only for testing purposes

    @staticmethod
    def from_model(userModel: UserModel) -> "UserPublicDTO":
        return UserPublicDTO(
            id=userModel.id,
            username=userModel.username,
            role=userModel.role,
            email=userModel.email,
            count=userModel.count
        )

class UserCreateDTO(UserBase):
    google_sub: str | None = None

class UserUpdateDTO(BaseModel):
    username: str | None = None
    role: str | None = None
    email: str | None = None
    google_sub: str | None = None




class LoggedInUserDTO(BaseModel):
    access_token: str
    refresh_token: str
    user_info: UserPublicDTO