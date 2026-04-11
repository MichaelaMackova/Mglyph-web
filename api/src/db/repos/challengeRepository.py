from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_, and_, case
from sqlalchemy.orm import selectinload, joinedload
from uuid import UUID
from db.repos.interface import RepositoryInterface
from db.pagination import paginate, PaginationParams, PagedResponse

from db.models.challengeModel import ChallengeModel
from db.models.challengeSolverModel import ChallengeSolverModel
from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel, ChallengeEvaluatorState
from db.models.mglyphEvaluatorModel import MGlyphEvaluatorModel
from db.models.answerModel import AnswerModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.malleableGlyphModel import MalleableGlyphModel


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
                state: list[tuple[bool, bool]] | None = None,
            ):
            """
            Args:
                name_contains (str | None): Filter challenges whose name contains the specified string (case-insensitive).
                state (list[tuple[bool, bool]] | None): List of tuples of (challenge_finished, submissions_ended).
            """
            self.name_contains = name_contains
            self.state = state

        def apply_filters_to_statement(self, statement):
            if self.name_contains:
                statement = statement.where(ChallengeModel.name.ilike(f"%{self.name_contains}%"))
            if self.state:
                and_conditions = []
                for challenge_finished, submissions_ended in self.state:
                    and_conditions.append(and_(ChallengeModel.challenge_finished == challenge_finished, ChallengeModel.submissions_ended == submissions_ended))
                if and_conditions:
                    statement = statement.where(or_(*and_conditions))
                
            return statement

    async def get_challenge_by_id(self, challenge_id: UUID, load_options: LoadOptions = LoadOptions()) -> ChallengeModel | None:
        select_exec = select(ChallengeModel).where(ChallengeModel.id == challenge_id)
        select_exec = load_options.add_options_to_statement(select_exec)
        result = await self.db_session.execute(select_exec)
        challenge_db = result.scalar_one_or_none()
        return challenge_db

    async def validate_unique_challenge_params(self, name: str, exclude_challenge_id: UUID | None = None) -> bool:
        select_exec = select(ChallengeModel).where(ChallengeModel.name == name)
        if exclude_challenge_id:
            select_exec = select_exec.where(ChallengeModel.id != exclude_challenge_id)
        result = await self.db_session.execute(select_exec)
        existing_challenge = result.scalar_one_or_none()
        return existing_challenge is None

    async def get_paginated_challenges(self, filters: FilterParams = FilterParams(), page: int = 1, size: int = 20, load_options: LoadOptions = LoadOptions()) -> PagedResponse[ChallengeModel]:
        select_exec = select(ChallengeModel)
        select_exec = filters.apply_filters_to_statement(select_exec)
        select_exec = load_options.add_options_to_statement(select_exec)
        pagination_params = PaginationParams(page=page, size=size)
        result = await paginate(self.db_session, select_exec, ChallengeModel, pagination_params)
        return result

    async def get_user_relationship_for_challenges(self, user_id: UUID | None = None, challenge_ids: list[UUID] | None = None) -> dict[UUID, dict[str, bool]]:
        """
        Returns:
            dict:
                - key: challenge_id
                - value: dict with keys:
                    is_solver: bool
                    has_submitted_mglyph: bool
                    is_evaluator: bool
                    waiting_for_evaluation: bool
        """
        mglyph_evaluator_without_answer_exists_subq = select(MGlyphEvaluatorModel.id)\
            .join(ChallengeEvaluatorModel, and_(
                MGlyphEvaluatorModel.challenge_evaluator_id == ChallengeEvaluatorModel.id,
                ChallengeEvaluatorModel.challenge_id == ChallengeModel.id,
                ChallengeEvaluatorModel.evaluator_id == user_id,
            ))\
            .outerjoin(AnswerModel, AnswerModel.mglyph_evaluator_id == MGlyphEvaluatorModel.id)\
            .where(AnswerModel.id.is_(None)).exists()

        submitted_mglyph_exists_subq = select(MGlyphEvaluationModel.malleable_glyph_id)\
            .join(EvaluationRoundModel, and_(MGlyphEvaluationModel.evaluation_round_id == EvaluationRoundModel.id, EvaluationRoundModel.challenge_id == ChallengeModel.id, EvaluationRoundModel.sequence_number == 1))\
            .join(MalleableGlyphModel, and_(MGlyphEvaluationModel.malleable_glyph_id == MalleableGlyphModel.id, MalleableGlyphModel.submission_time.is_not(None), MalleableGlyphModel.creator_id == user_id))\
            .exists()
        
        select_exec = select(
                        ChallengeModel.id,
                        case(
                            (user_id is None, False),
                            (ChallengeSolverModel.solver_id == user_id, True),
                            else_=False).label("is_solver"),
                        case(
                            (submitted_mglyph_exists_subq, True),
                            else_=False).label("has_submitted_mglyph"),
                        case(
                            (user_id is None, False),
                            (ChallengeEvaluatorModel.evaluator_id == user_id, True),
                            else_=False).label("is_evaluator"),
                        case(
                            (mglyph_evaluator_without_answer_exists_subq, True),
                            else_=False).label("waiting_for_evaluation")
                    )\
            .outerjoin(ChallengeSolverModel, and_(ChallengeSolverModel.challenge_id == ChallengeModel.id, ChallengeSolverModel.solver_id == user_id))\
            .outerjoin(ChallengeEvaluatorModel, and_(ChallengeEvaluatorModel.challenge_id == ChallengeModel.id, ChallengeEvaluatorModel.evaluator_id == user_id, ChallengeEvaluatorModel.state == ChallengeEvaluatorState.confirmed))\
            .where(ChallengeModel.id.in_(challenge_ids))
        
        result = await self.db_session.execute(select_exec)
        user_relationships = result.all()

        user_relationships_per_challenge = {}
        for challenge_id, is_solver, has_submitted_mglyph, is_evaluator, waiting_for_evaluation in user_relationships:
            user_relationships_per_challenge[challenge_id] = {
                "is_solver": is_solver,
                "has_submitted_mglyph": has_submitted_mglyph,
                "is_evaluator": is_evaluator,
                "waiting_for_evaluation": waiting_for_evaluation
            }
        return user_relationships_per_challenge


    async def get_paginated_challenges_with_participating_user(self, user_id: UUID, as_solver: bool | None = None, filters: FilterParams = FilterParams(), page: int = 1, size: int = 20, load_options: LoadOptions = LoadOptions()) -> PagedResponse[ChallengeModel]:
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
        select_exec = filters.apply_filters_to_statement(select_exec)
        select_exec = load_options.add_options_to_statement(select_exec)

        pagination_params = PaginationParams(page=page, size=size)
        paginated_challenges_db = await paginate(self.db_session, select_exec, ChallengeModel, pagination_params)
        return paginated_challenges_db
    

def get_challenge_repository(db_session: SessionDep):
    return ChallengeRepository(db_session)

ChallengeRepositoryDep = Annotated[ChallengeRepository, Depends(get_challenge_repository)]