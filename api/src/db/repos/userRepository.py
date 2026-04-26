from typing import Annotated, Optional
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import Select
from uuid import UUID
from db.repos.interface import RepositoryInterface
from db.pagination import paginate, PaginationParams, PagedResponse

from db.models.userModel import UserModel, UserRole

from api.users.schemas import UserCreateDTO



class UserRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(
                self, 
                load_solver_challenges: bool = False,
                load_challenge_evaluator_links: bool = False,
                load_malleable_glyphs: bool = False,
                load_created_challenges: bool = False,
                load_reported_flags: bool = False,
                load_resolved_flags: bool = False
            ):
            self.load_solver_challenges = load_solver_challenges
            self.load_challenge_evaluator_links = load_challenge_evaluator_links
            self.load_malleable_glyphs = load_malleable_glyphs
            self.load_created_challenges = load_created_challenges
            self.load_reported_flags = load_reported_flags
            self.load_resolved_flags = load_resolved_flags

        @staticmethod
        def all_options() -> "UserRepository.LoadOptions":
            return UserRepository.LoadOptions(
                load_solver_challenges=True,
                load_challenge_evaluator_links=True,
                load_malleable_glyphs=True,
                load_created_challenges=True,
                load_reported_flags=True,
                load_resolved_flags=True
            )

        def add_options_to_statement(self, statement):
            if self.load_solver_challenges:
                statement = statement.options(selectinload(UserModel.solver_challenges))
            if self.load_challenge_evaluator_links:
                statement = statement.options(selectinload(UserModel.challenge_evaluator_links))
            if self.load_malleable_glyphs:
                statement = statement.options(selectinload(UserModel.malleable_glyphs))
            if self.load_created_challenges:
                statement = statement.options(selectinload(UserModel.created_challenges))
            if self.load_reported_flags:
                statement = statement.options(selectinload(UserModel.reported_flags))
            if self.load_resolved_flags:
                statement = statement.options(selectinload(UserModel.resolved_flags))
            return statement

    class FilterParams():
        def __init__(
                self, 
                username_contains: Optional[str] = None,
                email_contains: Optional[str] = None,
                is_admin: Optional[bool] = None
            ):
            self.username_contains = username_contains
            self.email_contains = email_contains
            self.is_admin = is_admin

        def apply_filters_to_statement(self, statement: Select) -> Select:
            if self.username_contains:
                statement = statement.where(UserModel.username.ilike(f"%{self.username_contains}%"))
            if self.email_contains:
                statement = statement.where(UserModel.email.ilike(f"%{self.email_contains}%"))
            if self.is_admin is not None:
                if self.is_admin:
                    statement = statement.where(UserModel.role == UserRole.admin)
                else:
                    statement = statement.where(UserModel.role != UserRole.admin)
            return statement

    async def get_user_by_id(self, user_id: UUID, load_options: LoadOptions = LoadOptions()) -> UserModel | None:
        select_exec = select(UserModel).where(UserModel.id == user_id)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        user_db = result.scalar_one_or_none()
        return user_db
    

    async def get_user_by_email(self, email: str, load_options: LoadOptions = LoadOptions()) -> UserModel | None:
        select_exec = select(UserModel).where(UserModel.email == email)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        user_db = result.scalar_one_or_none()
        return user_db
    

    async def get_user_by_google_sub(self, google_sub: str, load_options: LoadOptions = LoadOptions()) -> UserModel | None:
        select_exec = select(UserModel).where(UserModel.google_sub == google_sub)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        user_db = result.scalar_one_or_none()
        return user_db
    

    async def get_user_by_username(self, username: str, load_options: LoadOptions = LoadOptions()) -> UserModel | None:
        select_exec = select(UserModel).where(UserModel.username == username)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        user_db = result.scalar_one_or_none()
        return user_db


    async def get_paginated_users(self, filters: FilterParams = FilterParams(), page: int = 1, size: int = 20, load_options: LoadOptions = LoadOptions()) -> PagedResponse[UserModel]:
        select_exec = select(UserModel)
        select_exec = filters.apply_filters_to_statement(select_exec)
        select_exec = load_options.add_options_to_statement(select_exec)
        return await paginate(self.db_session, select_exec, UserModel, PaginationParams(page=page, size=size), as_scalar=True)


    async def count_users_by_role(self, role: UserRole) -> int:
        select_exec = select(func.count()).select_from(UserModel).where(UserModel.role == role)
        result = await self.db_session.execute(select_exec)
        count = result.scalar_one()
        return count
    


def get_user_repository(db_session: SessionDep):
    return UserRepository(db_session)

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]