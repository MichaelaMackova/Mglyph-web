from typing import Annotated, Optional
from pydantic import BaseModel
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import Select
from uuid import UUID
from enum import Enum
from db.repos.interface import RepositoryInterface

from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.malleableGlyphModel import MalleableGlyphModel


class MGlyphEvaluationRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_malleable_glyph: bool = False, load_evaluation_round: bool = False, load_mglyph_evaluator_links: bool = False, load_malleable_glyph_creator: bool = False):
            self.load_malleable_glyph = load_malleable_glyph
            self.load_evaluation_round = load_evaluation_round
            self.load_mglyph_evaluator_links = load_mglyph_evaluator_links
            self.load_malleable_glyph_creator = load_malleable_glyph_creator

        @staticmethod
        def all_options():
            return MGlyphEvaluationRepository.LoadOptions(load_malleable_glyph=True, load_evaluation_round=True, load_mglyph_evaluator_links=True, load_malleable_glyph_creator=True)

        def add_options_to_statement(self, statement: Select) -> Select:
            if self.load_malleable_glyph:
                load_expr = joinedload(MGlyphEvaluationModel.malleable_glyph)
                if self.load_malleable_glyph_creator:
                    load_expr = load_expr.joinedload(MalleableGlyphModel.creator)
                statement = statement.options(load_expr)
            if self.load_evaluation_round:
                statement = statement.options(joinedload(MGlyphEvaluationModel.evaluation_round))
            if self.load_mglyph_evaluator_links:
                statement = statement.options(selectinload(MGlyphEvaluationModel.mglyph_evaluator_links))
            return statement
        
    class OrderByOption(Enum):
        RANK_ASC = 'rank'
        RANK_DESC = 'rank_desc'


    async def get_paginated_mglyph_evaluations_in_challenge_round(self, evaluation_round_id: UUID, only_submitted: bool = True, order_by: OrderByOption = OrderByOption.RANK_ASC, offset: int = 0, limit: int = 100, load_options: LoadOptions = LoadOptions()) -> list[MGlyphEvaluationModel]:
        select_exec = select(MGlyphEvaluationModel).where(MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id)
        if only_submitted:
            select_exec = select_exec.join(MalleableGlyphModel).where(MalleableGlyphModel.submission_time.is_not(None))
        if order_by == MGlyphEvaluationRepository.OrderByOption.RANK_ASC:
            select_exec = select_exec.order_by(MGlyphEvaluationModel.rank.asc())
        elif order_by == MGlyphEvaluationRepository.OrderByOption.RANK_DESC:
            select_exec = select_exec.order_by(MGlyphEvaluationModel.rank.desc())
        select_exec = load_options.add_options_to_statement(select_exec)
        select_exec = select_exec.offset(offset).limit(limit)
        result = await self.db_session.execute(select_exec)
        return result.scalars().all()
    

def get_mglyph_evaluation_repository(db_session: SessionDep) -> MGlyphEvaluationRepository:
    return MGlyphEvaluationRepository(db_session)

MGlyphEvaluationRepositoryDep = Annotated[MGlyphEvaluationRepository, Depends(get_mglyph_evaluation_repository)]