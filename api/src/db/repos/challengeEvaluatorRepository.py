from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, case
from sqlalchemy import Select
from sqlalchemy.orm import selectinload, joinedload, aliased
from uuid import UUID
from enum import Enum
from db.repos.interface import RepositoryInterface
from db.pagination import paginate, PaginationParams, PagedResponse

from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel, InvitationType, InvitationState
from db.models.challengeModel import ChallengeModel



class ChallengeEvaluatorRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_challenge: bool = False, load_challenge_evaluation_rounds: bool = False, load_evaluator: bool = False, load_mglyph_evaluator_links: bool = False):
            self.load_challenge = load_challenge
            self.load_challenge_evaluation_rounds = load_challenge_evaluation_rounds
            self.load_evaluator = load_evaluator
            self.load_mglyph_evaluator_links = load_mglyph_evaluator_links
        
        @staticmethod
        def all_options() -> "ChallengeEvaluatorRepository.LoadOptions":
            return ChallengeEvaluatorRepository.LoadOptions(load_challenge=True, load_challenge_evaluation_rounds=True, load_evaluator=True, load_mglyph_evaluator_links=True)

        def add_options_to_statement(self, statement: Select) -> Select:
            if self.load_challenge:
                load_statement = joinedload(ChallengeEvaluatorModel.challenge)
                if self.load_challenge_evaluation_rounds:
                    load_statement = load_statement.selectinload(ChallengeModel.evaluation_rounds)
                statement = statement.options(load_statement)
            if self.load_evaluator:
                statement = statement.options(joinedload(ChallengeEvaluatorModel.evaluator))
            if self.load_mglyph_evaluator_links:
                statement = statement.options(selectinload(ChallengeEvaluatorModel.mglyph_evaluator_links))
            return statement

    class OrderByOption(Enum):
        CHALLENGE_NAME_ASC = "challenge_name_asc"
        CHALLENGE_NAME_DESC = "challenge_name_desc"
        INVITATION_TYPE_ASC = "invitation_type_asc"
        INVITATION_TYPE_DESC = "invitation_type_desc"
        INVITATION_STATE_ASC = "invitation_state_asc"
        INVITATION_STATE_DESC = "invitation_state_desc"

        @staticmethod
        def add_order_by_to_statement(order_by: set["ChallengeEvaluatorRepository.OrderByOption"], statement: Select, aliased_model: type[ChallengeEvaluatorModel] = ChallengeEvaluatorModel) -> Select:
            order_by_clauses = []
            for option in order_by:
                if option == ChallengeEvaluatorRepository.OrderByOption.CHALLENGE_NAME_ASC or option == ChallengeEvaluatorRepository.OrderByOption.CHALLENGE_NAME_DESC:
                    challenge_model_alias = aliased(ChallengeModel)
                    statement = statement.join(challenge_model_alias, challenge_model_alias.id == aliased_model.challenge_id)
                    if option == ChallengeEvaluatorRepository.OrderByOption.CHALLENGE_NAME_ASC:
                        order_by_clauses.append(challenge_model_alias.name.asc())
                    else:
                        order_by_clauses.append(challenge_model_alias.name.desc())
                elif option == ChallengeEvaluatorRepository.OrderByOption.INVITATION_TYPE_ASC or option == ChallengeEvaluatorRepository.OrderByOption.INVITATION_TYPE_DESC:
                    invitation_type_case = case(
                        (aliased_model.invitation_type == InvitationType.volunteer, 1),
                        (aliased_model.invitation_type == InvitationType.invited, 2),
                        else_=3
                    )
                    if option == ChallengeEvaluatorRepository.OrderByOption.INVITATION_TYPE_ASC:
                        order_by_clauses.append(invitation_type_case.asc())
                    else:
                        order_by_clauses.append(invitation_type_case.desc())
                elif option == ChallengeEvaluatorRepository.OrderByOption.INVITATION_STATE_ASC or option == ChallengeEvaluatorRepository.OrderByOption.INVITATION_STATE_DESC:
                    invitation_state_case = case(
                        (aliased_model.invitation_state == InvitationState.pending, 1),
                        (aliased_model.invitation_state == InvitationState.confirmed, 2),
                        (aliased_model.invitation_state == InvitationState.rejected, 3),
                        else_=4
                    )
                    if option == ChallengeEvaluatorRepository.OrderByOption.INVITATION_STATE_ASC:
                        order_by_clauses.append(invitation_state_case.asc())
                    else:
                        order_by_clauses.append(invitation_state_case.desc())
            if order_by_clauses:
                statement = statement.order_by(*order_by_clauses)
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

    async def get_paginated_challenge_evaluators_by_challenge_id(self, challenge_id: UUID, page: int = 1, size: int = 20, order_by: set[OrderByOption] = None, load_options: LoadOptions = LoadOptions()) -> PagedResponse[ChallengeEvaluatorModel]:
        statement = select(ChallengeEvaluatorModel).where(ChallengeEvaluatorModel.challenge_id == challenge_id)
        if order_by:
            statement = ChallengeEvaluatorRepository.OrderByOption.add_order_by_to_statement(order_by, statement)
        statement = load_options.add_options_to_statement(statement)
        pagination_params = PaginationParams(page=page, size=size)
        result = await paginate(self.db_session, statement, ChallengeEvaluatorModel, pagination_params)
        return result

    async def get_paginated_challenge_evaluators_by_user_id(self, user_id: UUID, page: int = 1, size: int = 20, order_by: set[OrderByOption] = None, load_options: LoadOptions = LoadOptions()) -> PagedResponse[ChallengeEvaluatorModel]:
        statement = select(ChallengeEvaluatorModel).where(ChallengeEvaluatorModel.evaluator_id == user_id)
        if order_by:
            statement = ChallengeEvaluatorRepository.OrderByOption.add_order_by_to_statement(order_by, statement)
        statement = load_options.add_options_to_statement(statement)
        pagination_params = PaginationParams(page=page, size=size)
        result = await paginate(self.db_session, statement, ChallengeEvaluatorModel, pagination_params)
        return result


def get_challenge_evaluator_repository(db_session: SessionDep):
    return ChallengeEvaluatorRepository(db_session)

ChallengeEvaluatorRepositoryDep = Annotated[ChallengeEvaluatorRepository, Depends(get_challenge_evaluator_repository)]