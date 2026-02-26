from typing import Annotated
from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import SessionDep
from uuid import UUID
import errors as mglyph_errors

from db.models.userModel import UserModel, UserRole

from db.repos.userRepository import UserRepository, UserRepositoryDep

from api.users.schemas import UserPublicDTO, UserCreateDTO, UserUpdateDTO




class UserService:
    def __init__(
            self, 
            db_session: AsyncSession, 
            user_repository: UserRepository
            ):
        self.db_session = db_session
        self.user_repository = user_repository

    
    async def get_paginated_users(self, offset: int = 0, limit: int = 100) -> list[UserModel]:
        return await self.user_repository.get_paginated_users(offset=offset, limit=limit)
    
    async def get_user_by_id(self, user_id: UUID) -> UserModel:
        user_db = await self.user_repository.get_user_by_id(user_id, load_options=UserRepository.LoadOptions(True, True, True, True, True, True))
        if not user_db:
            raise mglyph_errors.NotFoundError("User")
        return user_db
    
    async def give_admin_role(self, user_id: UUID) -> UserModel:
        user_db = await self.user_repository.get_user_by_id(user_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User")
        if user_db.role == UserRole.admin:
            raise mglyph_errors.BadRequestError("User already has admin role")
        user_db.role = UserRole.admin
        self.db_session.add(user_db)
        await self.db_session.commit()
        user_db = await self.user_repository.get_user_by_id(user_id)
        return user_db
    
    async def revoke_admin_role(self, user_id: UUID) -> UserModel:
        user_db = await self.user_repository.get_user_by_id(user_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User")
        if user_db.role != UserRole.admin:
            raise mglyph_errors.BadRequestError("User already does not have admin role")
        user_db.role = UserRole.user
        self.db_session.add(user_db)
        await self.db_session.commit()
        user_db = await self.user_repository.get_user_by_id(user_id)
        return user_db
    



def get_user_service(db_session: SessionDep, user_repository: UserRepositoryDep):
    return UserService(db_session, user_repository)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]