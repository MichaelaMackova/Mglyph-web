from typing import Annotated
from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import SessionDep
from uuid import UUID
import errors as mglyph_errors
from settings import AT_LEAST_ONE_ADMIN_USER, FIRST_USER_IS_ADMIN

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
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        return user_db
    
    async def give_admin_role(self, user_id: UUID) -> UserModel:
        user_db = await self.user_repository.get_user_by_id(user_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if user_db.role == UserRole.admin:
            raise mglyph_errors.BadRequestError("User already has admin role", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        user_db.role = UserRole.admin
        self.db_session.add(user_db)
        await self.db_session.commit()
        user_db = await self.user_repository.get_user_by_id(user_id)
        return user_db
    
    async def revoke_admin_role(self, user_id: UUID) -> UserModel:
        user_db = await self.user_repository.get_user_by_id(user_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if user_db.role != UserRole.admin:
            raise mglyph_errors.BadRequestError("User already does not have admin role", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        if AT_LEAST_ONE_ADMIN_USER:
            admin_count = await self.user_repository.count_users_by_role(UserRole.admin)
            if admin_count <= 1:
                raise mglyph_errors.BadRequestError("Cannot revoke admin role from the last admin user", mglyph_errors.ErrorCode.BAD_REQUEST_REVOKE_LAST_ADMIN)
        user_db.role = UserRole.user
        self.db_session.add(user_db)
        await self.db_session.commit()
        user_db = await self.user_repository.get_user_by_id(user_id)
        return user_db
    

    async def create_user(self, user_create: UserCreateDTO) -> UserModel:
        try:
            user_data = user_create.model_dump()
            user_db = UserModel.model_validate(user_data)
            user_db.id = None  # Ensure ID is None for new records
        except ValidationError as e:
            raise mglyph_errors.BadRequestError(f"Invalid user data: {e}")
        # check if email already exists
        existing_user = await self.user_repository.get_user_by_email(user_db.email)
        if existing_user:
            raise mglyph_errors.BadRequestError("User with this email already exists", mglyph_errors.ErrorCode.BAD_REQUEST_CREATE_USER_EMAIL_TAKEN)
        # check if google sub already exists
        if user_db.google_sub:
            existing_user = await self.user_repository.get_user_by_google_sub(user_db.google_sub)
            if existing_user:
                raise mglyph_errors.BadRequestError("User with this Google sub already exists", mglyph_errors.ErrorCode.BAD_REQUEST_CREATE_USER_GOOGLE_SUB_TAKEN)
        # check if username already exists
        existing_user = await self.user_repository.get_user_by_username(user_db.username)
        if existing_user:
            raise mglyph_errors.BadRequestError("User with this username already exists", mglyph_errors.ErrorCode.BAD_REQUEST_CREATE_USER_USERNAME_TAKEN)
        if FIRST_USER_IS_ADMIN:
            admin_count = await self.user_repository.count_users_by_role(UserRole.admin)
            if admin_count == 0:
                user_db.role = UserRole.admin
        self.db_session.add(user_db)
        await self.db_session.commit()
        user_db = await self.user_repository.get_user_by_id(user_db.id)
        return user_db
    



def get_user_service(db_session: SessionDep, user_repository: UserRepositoryDep):
    return UserService(db_session, user_repository)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]