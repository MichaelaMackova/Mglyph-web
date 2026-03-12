from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID
from db.repos.interface import RepositoryInterface

from db.models.challengeModel import ChallengeModel
from db.models.challengeSolverModel import ChallengeSolverModel
from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel


class ChallengeRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_creator: bool = False, load_solvers: bool = False, load_challenge_evaluator_links: bool = False, load_evaluation_rounds: bool = False):
            self.load_creator = load_creator
            self.load_solvers = load_solvers
            self.load_challenge_evaluator_links = load_challenge_evaluator_links
            self.load_evaluation_rounds = load_evaluation_rounds

        @staticmethod
        def all_options() -> "ChallengeRepository.LoadOptions":
            return ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True)

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

    class FilterParams():
        def __init__(
                self, 
                name_contains: str | None = None,
                submissions_ended: bool | None = None, 
                challenge_finished: bool | None = None
            ):
            self.name_contains = name_contains
            self.submissions_ended = submissions_ended
            self.challenge_finished = challenge_finished

        def apply_filters_to_statement(self, statement):
            if self.name_contains:
                statement = statement.where(ChallengeModel.name.ilike(f"%{self.name_contains}%"))
            if self.submissions_ended is not None:
                statement = statement.where(ChallengeModel.submissions_ended == self.submissions_ended)
            if self.challenge_finished is not None:
                statement = statement.where(ChallengeModel.challenge_finished == self.challenge_finished)
            return statement

    async def get_challenge_by_id(self, challenge_id: UUID, load_options: LoadOptions = LoadOptions()) -> ChallengeModel | None:
        select_exec = select(ChallengeModel).where(ChallengeModel.id == challenge_id)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        challenge_db = result.scalar_one_or_none()
        return challenge_db

    async def get_paginated_challenges(self, filters: FilterParams = FilterParams(), offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[ChallengeModel]:
        select_exec = select(ChallengeModel).offset(offset).limit(limit)
        select_exec = filters.apply_filters_to_statement(select_exec)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        challenges_db = result.scalars().all()
        return challenges_db
    
    async def get_paginated_challenges_with_participating_user(self, user_id: UUID, as_solver: bool | None = None, filters: FilterParams = FilterParams(), offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[ChallengeModel]:
        """
        If as_solver is True, returns paginated challenges where user is a solver. If as_solver is False, returns paginated challenges where user is an evaluator. If as_solver is None, returns paginated challenges where user is either a solver or an evaluator.
        """
        select_exec = select(ChallengeModel).distinct()
        if as_solver is None or as_solver:
            select_exec = select_exec\
                .outerjoin(ChallengeSolverModel, ChallengeSolverModel.challenge_id == ChallengeModel.id)
        if as_solver is None or not as_solver:
            select_exec = select_exec\
                .outerjoin(ChallengeEvaluatorModel, ChallengeEvaluatorModel.challenge_id == ChallengeModel.id)
        
        if as_solver is None:
            select_exec = select_exec.where(or_(ChallengeSolverModel.solver_id == user_id, ChallengeEvaluatorModel.evaluator_id == user_id))
        elif as_solver:
            select_exec = select_exec.where(ChallengeSolverModel.solver_id == user_id)
        else:
            select_exec = select_exec.where(ChallengeEvaluatorModel.evaluator_id == user_id)
        select_exec = select_exec.offset(offset).limit(limit)
        select_exec = filters.apply_filters_to_statement(select_exec)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        challenges_db = result.scalars().all()
        return challenges_db
    

def get_challenge_repository(db_session: SessionDep):
    return ChallengeRepository(db_session)

ChallengeRepositoryDep = Annotated[ChallengeRepository, Depends(get_challenge_repository)]