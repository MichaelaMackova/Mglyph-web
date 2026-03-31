from typing import Annotated, Optional
from pydantic import BaseModel
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_
from sqlalchemy.orm import selectinload, joinedload, aliased, contains_eager
from sqlalchemy import Select
from uuid import UUID
from enum import Enum
from db.repos.interface import RepositoryInterface
from db.pagination import paginate, PaginationParams, PagedResponse

from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.malleableGlyphModel import MalleableGlyphModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.challengeModel import ChallengeModel


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

        def add_options_to_statement(self, statement: Select, aliased_model: type[MGlyphEvaluationModel] = MGlyphEvaluationModel) -> Select:
            if self.load_malleable_glyph:
                load_expr = joinedload(aliased_model.malleable_glyph)
                if self.load_malleable_glyph_creator:
                    load_expr = load_expr.joinedload(MalleableGlyphModel.creator)
                statement = statement.options(load_expr)
            if self.load_evaluation_round:
                statement = statement.options(joinedload(aliased_model.evaluation_round))
            if self.load_mglyph_evaluator_links:
                statement = statement.options(selectinload(aliased_model.mglyph_evaluator_links))
            return statement
        
    class OrderByOption(Enum):
        RANK_ASC = 'rank'
        RANK_DESC = 'rank_desc'


    async def get_paginated_mglyph_evaluations_in_challenge_round(self, evaluation_round_id: UUID, only_submitted: bool = True, order_by: OrderByOption = OrderByOption.RANK_ASC, page: int = 1, size: int = 20, load_options: LoadOptions = LoadOptions()) -> PagedResponse[MGlyphEvaluationModel]:
        select_exec = select(MGlyphEvaluationModel).where(MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id)
        if only_submitted:
            select_exec = select_exec.join(MalleableGlyphModel).where(MalleableGlyphModel.submission_time.is_not(None))
        if order_by == MGlyphEvaluationRepository.OrderByOption.RANK_ASC:
            select_exec = select_exec.order_by(MGlyphEvaluationModel.rank.asc().nulls_last())
        elif order_by == MGlyphEvaluationRepository.OrderByOption.RANK_DESC:
            select_exec = select_exec.order_by(MGlyphEvaluationModel.rank.desc().nulls_first())
        select_exec = load_options.add_options_to_statement(select_exec)
        return await paginate(self.db_session, select_exec, MGlyphEvaluationModel, PaginationParams(page=page, size=size), as_scalar=True)


    async def get_mglyph_evaluations_in_challenges(
            self, 
            challenge_ids: list[UUID], 
            only_submitted: bool = True, 
            order_by: OrderByOption = OrderByOption.RANK_ASC, 
            limit_per_challenge: int = 5, 
            load_options: LoadOptions = LoadOptions()
    ) -> dict[UUID, list[MGlyphEvaluationModel]]:
        order_exec = None
        if order_by == MGlyphEvaluationRepository.OrderByOption.RANK_ASC:
            order_exec = MGlyphEvaluationModel.rank.asc().nulls_last()
        elif order_by == MGlyphEvaluationRepository.OrderByOption.RANK_DESC:
            order_exec = MGlyphEvaluationModel.rank.desc().nulls_first()
        ranked_glyphs_subselect = select(MGlyphEvaluationModel, 
                                         func.row_number().over(partition_by=EvaluationRoundModel.challenge_id, order_by=order_exec).label('row_num'),
                                         EvaluationRoundModel.challenge_id.label('challenge_id'))\
            .join(EvaluationRoundModel, and_(EvaluationRoundModel.id == MGlyphEvaluationModel.evaluation_round_id, EvaluationRoundModel.next_round_id.is_(None)))\
            .join(MalleableGlyphModel, MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id)
        if only_submitted:
            ranked_glyphs_subselect = ranked_glyphs_subselect.where(MalleableGlyphModel.submission_time.is_not(None))
        ranked_glyphs_subselect = ranked_glyphs_subselect.subquery()
        aliased_mglyph_evaluation = aliased(MGlyphEvaluationModel, ranked_glyphs_subselect)

        select_exec = select(ChallengeModel.id, aliased_mglyph_evaluation)\
            .outerjoin_from(ChallengeModel, ranked_glyphs_subselect, and_(ranked_glyphs_subselect.c.challenge_id == ChallengeModel.id, ranked_glyphs_subselect.c.row_num <= limit_per_challenge))\
            .where(ChallengeModel.id.in_(challenge_ids))
        
        if order_by == MGlyphEvaluationRepository.OrderByOption.RANK_ASC:
            select_exec = select_exec.order_by(aliased_mglyph_evaluation.rank.asc().nulls_last())
        elif order_by == MGlyphEvaluationRepository.OrderByOption.RANK_DESC:
            select_exec = select_exec.order_by(aliased_mglyph_evaluation.rank.desc().nulls_first())
        
        select_exec = load_options.add_options_to_statement(select_exec, aliased_model=aliased_mglyph_evaluation)

        sql_result = await self.db_session.execute(select_exec)
        mglyph_evaluations = sql_result.all()
        mglyph_evaluations_per_challenge = {}
        for challenge_id, mglyph_evaluation in mglyph_evaluations:
            if challenge_id not in mglyph_evaluations_per_challenge:
                mglyph_evaluations_per_challenge[challenge_id] = []
            if mglyph_evaluation is not None:
                mglyph_evaluations_per_challenge[challenge_id].append(mglyph_evaluation)
        return mglyph_evaluations_per_challenge
        



def get_mglyph_evaluation_repository(db_session: SessionDep) -> MGlyphEvaluationRepository:
    return MGlyphEvaluationRepository(db_session)

MGlyphEvaluationRepositoryDep = Annotated[MGlyphEvaluationRepository, Depends(get_mglyph_evaluation_repository)]