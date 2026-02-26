from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from db.models.userModel import UserModel, UserRole



class UserBase(BaseModel):
    username: str
    email: str

class UserPublicSimpleDTO(UserBase):
    id: UUID
    role: UserRole
    creation_time: datetime

    @staticmethod
    def from_model(userModel: UserModel) -> "UserPublicSimpleDTO":
        return UserPublicSimpleDTO(
            id=userModel.id,
            username=userModel.username,
            role=userModel.role,
            email=userModel.email,
            creation_time=userModel.creation_time
        )

class UserPublicDTO(UserBase):
    id: UUID
    role: UserRole
    creation_time: datetime
    count: int #TODO: remove this field, it's only for testing purposes

    @staticmethod
    def from_model(userModel: UserModel) -> "UserPublicDTO":
        return UserPublicDTO(
            id=userModel.id,
            username=userModel.username,
            role=userModel.role,
            email=userModel.email,
            creation_time=userModel.creation_time,
            count=userModel.count
        )

class UserCreateDTO(UserBase):
    google_sub: str | None

class UserUpdateDTO(BaseModel):
    username: str | None = None
    email: str | None = None
    google_sub: str | None = None