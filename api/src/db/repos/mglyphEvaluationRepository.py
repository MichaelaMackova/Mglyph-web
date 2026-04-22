from typing import Annotated, Optional
from pydantic import BaseModel
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, update, case, func, and_
from sqlalchemy.orm import selectinload, joinedload, aliased, contains_eager
from sqlalchemy import Select
from uuid import UUID
from enum import Enum
from db.repos.interface import RepositoryInterface
from db.pagination import paginate, PaginationParams, PagedResponse
from calculate_score import calculate_score, GroupedAnswerInfo

from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.malleableGlyphModel import MalleableGlyphModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.challengeModel import ChallengeModel
from db.models.userModel import UserModel
from db.models.mglyphEvaluatorModel import MGlyphEvaluatorModel
from db.models.answerModel import AnswerModel


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
        RANK_ASC = 'rank_asc'
        RANK_DESC = 'rank_desc'
        CREATOR_ASC = 'creator_asc'
        CREATOR_DESC = 'creator_desc'

        def add_order_by_to_statement(self, statement: Select, aliased_model: type[MGlyphEvaluationModel] = MGlyphEvaluationModel) -> Select:
            if self == MGlyphEvaluationRepository.OrderByOption.RANK_ASC:
                return statement.order_by(aliased_model.rank.asc().nulls_last())
            elif self == MGlyphEvaluationRepository.OrderByOption.RANK_DESC:
                return statement.order_by(aliased_model.rank.desc().nulls_first())
            elif self == MGlyphEvaluationRepository.OrderByOption.CREATOR_ASC or self == MGlyphEvaluationRepository.OrderByOption.CREATOR_DESC:
                MGlyphModelAliased = aliased(MalleableGlyphModel)
                UserModelAliased = aliased(UserModel)
                statement = statement.join(MGlyphModelAliased, aliased_model.malleable_glyph_id == MGlyphModelAliased.id).join(UserModelAliased, MGlyphModelAliased.creator_id == UserModelAliased.id)
                if self == MGlyphEvaluationRepository.OrderByOption.CREATOR_ASC:
                    return statement.order_by(UserModelAliased.username.asc())
                if self == MGlyphEvaluationRepository.OrderByOption.CREATOR_DESC:
                    return statement.order_by(UserModelAliased.username.desc())
            else:
                return statement


    async def get_paginated_mglyph_evaluations_in_challenge_round(self, evaluation_round_id: UUID, only_submitted: bool = True, order_by: OrderByOption | None = None, page: int = 1, size: int = 20, load_options: LoadOptions = LoadOptions()) -> PagedResponse[MGlyphEvaluationModel]:
        select_exec = select(MGlyphEvaluationModel).where(MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id)
        if only_submitted:
            select_exec = select_exec.join(MalleableGlyphModel).where(MalleableGlyphModel.submission_time.is_not(None))
        if order_by:
            select_exec = order_by.add_order_by_to_statement(select_exec)
        else:
            select_exec = select_exec.order_by(MGlyphEvaluationModel.id.asc())
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
        ranked_glyphs_subselect = select(MGlyphEvaluationModel, 
                                         func.row_number().over(partition_by=EvaluationRoundModel.challenge_id,).label('row_num'),
                                         EvaluationRoundModel.challenge_id.label('challenge_id'))\
            .join(EvaluationRoundModel, and_(EvaluationRoundModel.id == MGlyphEvaluationModel.evaluation_round_id, EvaluationRoundModel.next_round_id.is_(None)))\
            .join(MalleableGlyphModel, MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id)
        ranked_glyphs_subselect = order_by.add_order_by_to_statement(ranked_glyphs_subselect, aliased_model=MGlyphEvaluationModel)
        if only_submitted:
            ranked_glyphs_subselect = ranked_glyphs_subselect.where(MalleableGlyphModel.submission_time.is_not(None))
        ranked_glyphs_subselect = ranked_glyphs_subselect.subquery()
        aliased_mglyph_evaluation = aliased(MGlyphEvaluationModel, ranked_glyphs_subselect)

        select_exec = select(ChallengeModel.id, aliased_mglyph_evaluation)\
            .outerjoin_from(ChallengeModel, ranked_glyphs_subselect, and_(ranked_glyphs_subselect.c.challenge_id == ChallengeModel.id, ranked_glyphs_subselect.c.row_num <= limit_per_challenge))\
            .where(ChallengeModel.id.in_(challenge_ids))
        
        select_exec = order_by.add_order_by_to_statement(select_exec, aliased_model=aliased_mglyph_evaluation)
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
    

    async def get_mglyph_evaluations_for_evaluation_round_and_evaluator(
        self,
        evaluation_round_id: UUID,
        challenge_evaluator_id: UUID,
        only_submitted: bool = True,
        load_options: LoadOptions = LoadOptions()
    ) -> list[MGlyphEvaluationModel]:
        select_exec = select(MGlyphEvaluationModel)\
            .join(MGlyphEvaluatorModel)\
            .where(
                MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id,
                MGlyphEvaluatorModel.challenge_evaluator_id == challenge_evaluator_id
            )
        if only_submitted:
            select_exec = select_exec.join(MalleableGlyphModel, MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id)\
                .where(MalleableGlyphModel.submission_time.is_not(None))
        select_exec = load_options.add_options_to_statement(select_exec)
        sql_result = await self.db_session.execute(select_exec)
        return sql_result.scalars().all()


    async def bulk_update_score_of_mglyph_evaluations(self, mglyph_evaluation_scores: list[dict], commit: bool = True):
        """
        Args:
            mglyph_evaluation_scores (list[dict]): A list of dictionaries, where each dictionary has the following keys:
                - id (UUID): The id of the mglyph evaluation to update the score for
                - score (float): The new score to set for the mglyph evaluation
            commit (bool): Whether to commit the transaction after executing the update statement. Default is True.
        """
        await self.db_session.execute(update(MGlyphEvaluationModel), mglyph_evaluation_scores)
        if commit:
            await self.db_session.commit()

    async def get_mglyph_evaluations_score_calculation_helpers(self, evaluation_round_id: UUID, malleable_glyph_ids: list[UUID]) -> list[tuple[UUID, list[GroupedAnswerInfo]]]:
        """
        This is a helper function to get the data needed to calculate the score for mglyph evaluations. It returns a paginated list of tuples, where each tuple contains the mglyph evaluation id and a list of GroupedAnswerInfo objects (grouped by distance).
        """
        calculation_helpers_query = select(
            MGlyphEvaluationModel.id,
            AnswerModel.glyph_distance,
            func.count(AnswerModel.id).label('total_answers'),
            func.sum(
                case(
                    (AnswerModel.is_answer_correct == True, 1),
                    else_=0
                )
            ).label('correct_answers')
        ).join(MGlyphEvaluatorModel, MGlyphEvaluatorModel.mglyph_evaluation_id == MGlyphEvaluationModel.id)\
        .join(AnswerModel, AnswerModel.mglyph_evaluator_id == MGlyphEvaluatorModel.id)\
        .where(MGlyphEvaluationModel.malleable_glyph_id.in_(malleable_glyph_ids), MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id)\
        .group_by(MGlyphEvaluationModel.id, AnswerModel.glyph_distance)\
        .order_by(MGlyphEvaluationModel.id.asc(), AnswerModel.glyph_distance.asc())

        calculation_helpers_result = await self.db_session.execute(calculation_helpers_query)
        calculation_helpers_rows = calculation_helpers_result.all()

        # Group the results by mglyph evaluation id
        grouped_helpers : list[tuple[UUID, list[GroupedAnswerInfo]]] = []
        for mglyph_evaluation_id, glyph_distance, total_answers, correct_answers in calculation_helpers_rows:
            if len(grouped_helpers) == 0 or grouped_helpers[-1][0] != mglyph_evaluation_id:
                grouped_helpers.append((mglyph_evaluation_id, []))
            grouped_helpers[-1][1].append(GroupedAnswerInfo(distance=glyph_distance, count_total=total_answers, count_correct=correct_answers))
        
        return grouped_helpers

        
        
    async def update_rank_of_all_mglyph_evaluations_in_evaluation_round(self, evaluation_round_id: UUID, commit: bool = True):
        get_rank_subquery = select(
            MGlyphEvaluationModel.id,
            func.row_number().over(order_by=MGlyphEvaluationModel.score.desc().nulls_last()).label('rank')
        ).where(MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id)
        get_rank_subquery = get_rank_subquery.subquery()

        # Perform bulk update using the subquery
        update_stmt = update(MGlyphEvaluationModel).values(
            rank=get_rank_subquery.c.rank
        ).where(
            MGlyphEvaluationModel.id == get_rank_subquery.c.id,
            MGlyphEvaluationModel.evaluation_round_id == evaluation_round_id,
            MGlyphEvaluationModel.score.is_not(None)  # Only update rank for evaluations that have a score
        )

        await self.db_session.execute(update_stmt)
        if commit:
            await self.db_session.commit()



def get_mglyph_evaluation_repository(db_session: SessionDep) -> MGlyphEvaluationRepository:
    return MGlyphEvaluationRepository(db_session)

MGlyphEvaluationRepositoryDep = Annotated[MGlyphEvaluationRepository, Depends(get_mglyph_evaluation_repository)]