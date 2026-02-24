from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID

from db.models.evaluationRoundModel import EvaluationRoundModel


class EvaluationRoundRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions:
        def __init__(self, load_challenge: bool = False, load_next_round: bool = False, load_previous_round: bool = False, load_mglyph_evaluation_links: bool = False):
            self.load_challenge = load_challenge
            self.load_next_round = load_next_round
            self.load_previous_round = load_previous_round
            self.load_mglyph_evaluation_links = load_mglyph_evaluation_links

        def add_options_to_statement(self, statement):
            if self.load_challenge:
                statement = statement.options(joinedload(EvaluationRoundModel.challenge))
            if self.load_next_round:
                statement = statement.options(joinedload(EvaluationRoundModel.next_round))
            if self.load_previous_round:
                statement = statement.options(joinedload(EvaluationRoundModel.previous_round))
            if self.load_mglyph_evaluation_links:
                statement = statement.options(selectinload(EvaluationRoundModel.mglyph_evaluation_links))
            return statement

    async def get_first_round_in_challenge(self, challenge_id: UUID, load_options: LoadOptions = LoadOptions()) -> EvaluationRoundModel | None:
        select_exec = select(EvaluationRoundModel).where(EvaluationRoundModel.challenge_id == challenge_id).where(EvaluationRoundModel.sequence_number == 1)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        evaluation_round_db = result.scalar_one_or_none()
        return evaluation_round_db
    

def get_evaluation_round_repository(db_session: SessionDep):
    return EvaluationRoundRepository(db_session)

EvaluationRoundRepositoryDep = Annotated[EvaluationRoundRepository, Depends(get_evaluation_round_repository)]