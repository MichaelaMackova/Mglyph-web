from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import Select
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID
from db.repos.interface import RepositoryInterface

from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel



class ChallengeEvaluatorRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_challenge: bool = False, load_evaluator: bool = False, load_mglyph_evaluator_links: bool = False):
            self.load_challenge = load_challenge
            self.load_evaluator = load_evaluator
            self.load_mglyph_evaluator_links = load_mglyph_evaluator_links
        
        @staticmethod
        def all_options() -> "ChallengeEvaluatorRepository.LoadOptions":
            return ChallengeEvaluatorRepository.LoadOptions(load_challenge=True, load_evaluator=True, load_mglyph_evaluator_links=True)

        def add_options_to_statement(self, statement: Select) -> Select:
            if self.load_challenge:
                statement = statement.options(joinedload(ChallengeEvaluatorModel.challenge))
            if self.load_evaluator:
                statement = statement.options(joinedload(ChallengeEvaluatorModel.evaluator))
            if self.load_mglyph_evaluator_links:
                statement = statement.options(selectinload(ChallengeEvaluatorModel.mglyph_evaluator_links))
            return statement



    async def get_challenge_evaluator_by_id(self, id: UUID, load_options: LoadOptions = LoadOptions()) -> ChallengeEvaluatorModel | None:
        statement = select(ChallengeEvaluatorModel).where(ChallengeEvaluatorModel.id == id)
        statement = load_options.add_options_to_statement(statement)
        result = await self.db_session.execute(statement)
        return result.scalar_one_or_none()

    async def get_challenge_evaluator_by_challenge_id_and_evaluator_id(self, challenge_id: UUID, evaluator_user_id: UUID, load_options: LoadOptions = LoadOptions()) -> ChallengeEvaluatorModel | None:
        statement = select(ChallengeEvaluatorModel).where(
            ChallengeEvaluatorModel.challenge_id == challenge_id,
            ChallengeEvaluatorModel.evaluator_id == evaluator_user_id
        )
        statement = load_options.add_options_to_statement(statement)
        result = await self.db_session.execute(statement)
        return result.scalar_one_or_none()


def get_challenge_evaluator_repository(db_session: SessionDep):
    return ChallengeEvaluatorRepository(db_session)

ChallengeEvaluatorRepositoryDep = Annotated[ChallengeEvaluatorRepository, Depends(get_challenge_evaluator_repository)]