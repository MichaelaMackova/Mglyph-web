from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID

from db.models.userModel import UserModel

from api.users.schemas import UserCreateDTO



class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions:
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


    async def get_paginated_users(self, offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[UserModel]:
        select_exec = select(UserModel).offset(offset).limit(limit)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        users_db = result.scalars().all()
        return users_db
    


def get_user_repository(db_session: SessionDep):
    return UserRepository(db_session)

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]