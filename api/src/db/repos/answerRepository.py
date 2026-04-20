from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, insert, and_
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID
from db.repos.interface import RepositoryInterface

from db.models.answerModel import AnswerModel
from db.models.mglyphEvaluatorModel import MGlyphEvaluatorModel
from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel



class AnswerRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_mglyph_evaluator_link: bool = False):
            self.load_mglyph_evaluator_link = load_mglyph_evaluator_link

        @staticmethod
        def all_options() -> "AnswerRepository.LoadOptions":
            return AnswerRepository.LoadOptions(load_mglyph_evaluator_link=True)

        def add_options_to_statement(self, statement):
            if self.load_mglyph_evaluator_link:
                statement = statement.options(joinedload(AnswerModel.mglyph_evaluator_link))
            return statement

    async def get_answer_by_id(self, answer_id: UUID, load_options: LoadOptions = LoadOptions()) -> AnswerModel | None:
        select_exec = select(AnswerModel).where(AnswerModel.id == answer_id)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        answer_db = result.scalar_one_or_none()
        return answer_db

    async def bulk_insert(self, answers: list[dict], challenge_evaluator_id: UUID, evaluation_round_id: UUID):
        mglyph_evaluator_id_stmt = select(MGlyphEvaluatorModel.id)\
            .join(ChallengeEvaluatorModel, and_(MGlyphEvaluatorModel.challenge_evaluator_id == ChallengeEvaluatorModel.id, ChallengeEvaluatorModel.id == challenge_evaluator_id))\
            .join(MGlyphEvaluationModel, and_(MGlyphEvaluatorModel.mglyph_evaluation_id == MGlyphEvaluationModel.id, MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id))
        for answer in answers:
            answer["mglyph_evaluator_id"] = mglyph_evaluator_id_stmt.where(MGlyphEvaluationModel.malleable_glyph_id == answer.pop("malleable_glyph_id"))
        stmt = insert(AnswerModel).values(answers)
        await self.db_session.execute(stmt)


def get_answer_repository(db_session: SessionDep):
    return AnswerRepository(db_session)

AnswerRepositoryDep = Annotated[AnswerRepository, Depends(get_answer_repository)]