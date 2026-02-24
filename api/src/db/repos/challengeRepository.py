from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID

from db.models.challengeModel import ChallengeModel


class ChallengeRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions:
        def __init__(self, load_creator: bool = False, load_solvers: bool = False, load_challenge_evaluator_links: bool = False, load_evaluation_rounds: bool = False):
            self.load_creator = load_creator
            self.load_solvers = load_solvers
            self.load_challenge_evaluator_links = load_challenge_evaluator_links
            self.load_evaluation_rounds = load_evaluation_rounds

        def add_options_to_statement(self, statement):
            if self.load_creator:
                statement = statement.options(joinedload(ChallengeModel.creator))
            if self.load_solvers:
                statement = statement.options(selectinload(ChallengeModel.solvers))
            if self.load_challenge_evaluator_links:
                statement = statement.options(selectinload(ChallengeModel.challenge_evaluator_links))
            if self.load_evaluation_rounds:
                statement = statement.options(selectinload(ChallengeModel.evaluation_rounds))
            return statement


    async def get_challenge_by_id(self, challenge_id: UUID, load_options: LoadOptions = LoadOptions()) -> ChallengeModel | None:
        select_exec = select(ChallengeModel).where(ChallengeModel.id == challenge_id)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        challenge_db = result.scalar_one_or_none()
        return challenge_db

    async def get_paginated_challenges(self, offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[ChallengeModel]:
        select_exec = select(ChallengeModel).offset(offset).limit(limit)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        challenges_db = result.scalars().all()
        return challenges_db
    

def get_challenge_repository(db_session: SessionDep):
    return ChallengeRepository(db_session)

ChallengeRepositoryDep = Annotated[ChallengeRepository, Depends(get_challenge_repository)]