from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID
from db.repos.interface import RepositoryInterface

from db.models.malleableGlyphModel import MalleableGlyphModel
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.challengeModel import ChallengeModel



class MalleableGlyphRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_creator: bool = False, load_mglyph_evaluation_links: bool = False, load_report_flags: bool = False):
            self.load_creator = load_creator
            self.load_mglyph_evaluation_links = load_mglyph_evaluation_links
            self.load_report_flags = load_report_flags

        @staticmethod
        def all_options():
            return MalleableGlyphRepository.LoadOptions(load_creator=True, load_mglyph_evaluation_links=True, load_report_flags=True)

        def add_options_to_statement(self, statement):
            if self.load_creator:
                statement = statement.options(joinedload(MalleableGlyphModel.creator))
            if self.load_mglyph_evaluation_links:
                statement = statement.options(selectinload(MalleableGlyphModel.mglyph_evaluation_links))
            if self.load_report_flags:
                statement = statement.options(selectinload(MalleableGlyphModel.report_flags))
            return statement


    async def get_malleable_glyph_by_id(self, mglyph_id: UUID, load_options: LoadOptions = LoadOptions()) -> MalleableGlyphModel | None:
        select_exec = select(MalleableGlyphModel).where(MalleableGlyphModel.id == mglyph_id)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        mglyph_db = result.scalar_one_or_none()
        return mglyph_db

    async def get_paginated_malleable_glyphs(self, offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[MalleableGlyphModel]:
        select_exec = select(MalleableGlyphModel).offset(offset).limit(limit)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        mglyphs_db = result.scalars().all()
        return mglyphs_db

    async def get_paginated_malleable_glyphs_in_challenge_round(self, evaluation_round_id: UUID, offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[MalleableGlyphModel]:
        select_exec = select(MalleableGlyphModel).distinct()\
            .join(MGlyphEvaluationModel, MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id)\
            .join(EvaluationRoundModel, EvaluationRoundModel.id == MGlyphEvaluationModel.evaluation_round_id)\
            .where(EvaluationRoundModel.id == evaluation_round_id)
        select_exec = select_exec.offset(offset).limit(limit)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        mglyphs_db = result.scalars().all()
        return mglyphs_db
        pass

    async def get_paginated_malleable_glyphs_in_challenge(self, challenge_id: UUID, offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[MalleableGlyphModel]:
        select_exec = select(MalleableGlyphModel).distinct()\
            .join(MGlyphEvaluationModel, MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id)\
            .join(EvaluationRoundModel, EvaluationRoundModel.id == MGlyphEvaluationModel.evaluation_round_id)\
            .join(ChallengeModel, ChallengeModel.id == EvaluationRoundModel.challenge_id)\
            .where(ChallengeModel.id == challenge_id)
        select_exec = select_exec.offset(offset).limit(limit)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        mglyphs_db = result.scalars().all()
        return mglyphs_db
    
    async def does_user_have_mglyph_in_challenge(self, user_id: UUID, challenge_id: UUID) -> bool:
        select_exec = select(MalleableGlyphModel)\
            .join(MGlyphEvaluationModel, MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id)\
            .join(EvaluationRoundModel, EvaluationRoundModel.id == MGlyphEvaluationModel.evaluation_round_id)\
            .join(ChallengeModel, ChallengeModel.id == EvaluationRoundModel.challenge_id)\
            .where(ChallengeModel.id == challenge_id, MalleableGlyphModel.creator_id == user_id)
        result = await self.db_session.execute(select_exec)
        mglyphs_db = result.scalars().all()
        return True if mglyphs_db else False

def get_malleable_glyph_repository(db_session: SessionDep):
    return MalleableGlyphRepository(db_session)

MalleableGlyphRepositoryDep = Annotated[MalleableGlyphRepository, Depends(get_malleable_glyph_repository)]