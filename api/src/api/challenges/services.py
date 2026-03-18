from typing import Annotated
from fastapi import Depends, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from db.database import SessionDep
from uuid import UUID
from datetime import datetime, timedelta, timezone
import errors as mglyph_errors

from db.models.challengeModel import ChallengeModel
from db.models.userModel import UserModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel, ChallengeEvaluatorState
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel

from db.repos.challengeRepository import ChallengeRepository, ChallengeRepositoryDep
from db.repos.evaluationRoundRepository import EvaluationRoundRepository, EvaluationRoundRepositoryDep
from db.repos.challengeEvaluatorRepository import ChallengeEvaluatorRepository, ChallengeEvaluatorRepositoryDep
from db.repos.mglyphEvaluationRepository import MGlyphEvaluationRepository, MGlyphEvaluationRepositoryDep

from api.challenges.schemas import ChallengeFilterParams, ChallengePublicDTO, ChallengeCreateDTO, ChallengeUpdateDTO


class EvaluationRoundService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def create_initial_evaluation_round(self, challenge_id: UUID, estimated_end_time: datetime) -> EvaluationRoundModel:
        evaluation_round = EvaluationRoundModel(
            id=None,
            sequence_number=1,
            estimated_end_time=estimated_end_time,
            challenge_id=challenge_id
        )
        self.db_session.add(evaluation_round)
        await self.db_session.commit()
        await self.db_session.refresh(evaluation_round)
        return evaluation_round



def get_evaluation_round_service(db_session: SessionDep):
    return EvaluationRoundService(db_session)

EvaluationRoundServiceDep = Annotated[EvaluationRoundService, Depends(get_evaluation_round_service)]






class ChallengeEvaluatorService:
    def __init__(self, db_session: AsyncSession, challenge_evaluator_repository: ChallengeEvaluatorRepository):
        self.db_session = db_session
        self.challenge_evaluator_repository = challenge_evaluator_repository


    async def change_state_of_challenge_evaluator(self, challenge_id: UUID, evaluator_user_id: UUID, new_state: ChallengeEvaluatorState, confirm_old_state: ChallengeEvaluatorState | None = None):
        challenge_evaluator_db = await self.challenge_evaluator_repository.get_challenge_evaluator_by_challenge_id_and_evaluator_id(challenge_id, evaluator_user_id)
        if not challenge_evaluator_db:
            raise mglyph_errors.NotFoundError("Challenge Evaluator link", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if confirm_old_state is not None and challenge_evaluator_db.state != confirm_old_state:
            raise mglyph_errors.BadRequestError("Challenge Evaluator state does not match", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        challenge_evaluator_db.state = new_state
        self.db_session.add(challenge_evaluator_db)
        await self.db_session.commit()
        return challenge_evaluator_db


    async def create_challenge_evaluator(self, challenge_id: UUID, evaluator_user_id: UUID, is_volunteer: bool) -> ChallengeEvaluatorModel:
        new_challenge_evaluator = ChallengeEvaluatorModel(
            id=None,
            challenge_id=challenge_id,
            evaluator_id=evaluator_user_id,
            state=ChallengeEvaluatorState.volunteer_pending if is_volunteer else ChallengeEvaluatorState.invited_pending
        )
        self.db_session.add(new_challenge_evaluator)
        await self.db_session.commit()
        await self.db_session.refresh(new_challenge_evaluator)
        return new_challenge_evaluator

def get_challenge_evaluator_service(db_session: SessionDep, challenge_evaluator_repository: ChallengeEvaluatorRepositoryDep):
    return ChallengeEvaluatorService(db_session, challenge_evaluator_repository)

ChallengeEvaluatorServiceDep = Annotated[ChallengeEvaluatorService, Depends(get_challenge_evaluator_service)]








# TODO: přidat kontroly:
#           - challenge creation_time < glyph_submit_deadline < first evaluation round estimated_end_time
#           - při přidávání solvera zkontrolovat, že nejsou uzavřené submissiony
#           - při updatu zkontrolovat, že nenastane stav (submissions_ended = False and challenge_finished = True)
#           - při updatu zkontrolovat, že se nemění submissions_ended nebo challenge_finished z True na False

class ChallengeService:
    def __init__(
            self,
            db_session: AsyncSession,
            challenge_repository: ChallengeRepository,
            evaluation_round_repository: EvaluationRoundRepository,
            mglyph_evaluation_repository: MGlyphEvaluationRepository,
            evaluation_round_service: EvaluationRoundService,
            challenge_evaluator_service: ChallengeEvaluatorService,
        ):
        self.db_session = db_session
        self.challenge_repository = challenge_repository
        self.evaluation_round_repository = evaluation_round_repository
        self.mglyph_evaluation_repository = mglyph_evaluation_repository
        self.evaluation_round_service = evaluation_round_service
        self.challenge_evaluator_service = challenge_evaluator_service


    async def get_challenge_by_id(self, challenge_id: UUID) -> ChallengeModel:
        db_challenge = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        if not db_challenge:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        return db_challenge


    async def get_paginated_challenges_with_glyphs(self, filters: ChallengeFilterParams, glyph_count: int = 0, offset: int = 0, limit: int = 100) -> list[tuple[ChallengeModel, list[MGlyphEvaluationModel]]]:
        filter_params = ChallengeRepository.FilterParams(
            name_contains=filters.name_contains,
            submissions_ended=filters.submissions_ended,
            challenge_finished=filters.challenge_finished
        )
        challenges_db = await self.challenge_repository.get_paginated_challenges(filters=filter_params, offset=offset, limit=limit)
        challenges_with_glyphs = []
        for challenge in challenges_db:
            mglyphs = []
            if glyph_count > 0:
                last_round = await self.evaluation_round_repository.get_last_round_in_challenge(challenge.id)
                if last_round:
                    mglyphs = await self.mglyph_evaluation_repository.get_paginated_mglyph_evaluations_in_challenge_round(last_round.id, offset=0, limit=glyph_count, order_by=MGlyphEvaluationRepository.OrderByOption.RANK_ASC, load_options=MGlyphEvaluationRepository.LoadOptions(load_malleable_glyph=True, load_malleable_glyph_creator=True))
            challenges_with_glyphs.append((challenge, mglyphs))
        return challenges_with_glyphs


    async def get_challenges_where_user_is_participant(self, user_id: UUID, filters: ChallengeFilterParams, as_solver: bool | None = None, offset: int = 0, limit: int = 100) -> list[ChallengeModel]:
        filter_params = ChallengeRepository.FilterParams(
            name_contains=filters.name_contains,
            submissions_ended=filters.submissions_ended,
            challenge_finished=filters.challenge_finished
        )
        challenges_db = await self.challenge_repository.get_paginated_challenges_with_participating_user(user_id=user_id, filters=filter_params, as_solver=as_solver, offset=offset, limit=limit)
        return challenges_db


    async def create_challenge(self, challenge: ChallengeCreateDTO, current_user_id: UUID) -> ChallengeModel:
        # TODO: check if challenge name already exists
        try:
            challenge_data = challenge.model_dump()
            challenge_data["creator_id"] = current_user_id
            first_round_data = challenge_data.pop("first_evaluation_round")
            db_challenge = ChallengeModel.model_validate(challenge_data)
            db_challenge.id = None  # Ensure ID is None for new records
        except ValidationError as e:
            raise mglyph_errors.BadRequestError(f"Invalid challenge data: {e}")
        self.db_session.add(db_challenge)
        await self.db_session.flush()

        # Add first evaluation round
        await self.evaluation_round_service.create_initial_evaluation_round(db_challenge.id, first_round_data["estimated_end_time"])
        db_challenge = await self.challenge_repository.get_challenge_by_id(db_challenge.id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return db_challenge
    

    async def update_challenge(self, challenge_id: UUID, challenge_update: ChallengeUpdateDTO) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        challenge_data = challenge_update.model_dump(exclude_unset=True)
        challenge_db.sqlmodel_update(challenge_data)
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db
    

    async def delete_challenge(self, challenge_id: UUID):
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        first_round = await self.evaluation_round_repository.get_first_round_in_challenge(challenge_id, load_options=EvaluationRoundRepository.LoadOptions(load_mglyph_evaluation_links=True))
        if first_round:
            if first_round.mglyph_evaluation_links:
                raise mglyph_errors.BadRequestError("Cannot delete challenge with existing assigned malleable glyphs", mglyph_errors.ErrorCode.BAD_REQUEST_DELETE_CONFLICT)
        await self.db_session.delete(challenge_db)
        await self.db_session.commit()
    

    async def add_solver_to_challenge(self, challenge_id: UUID, solver_id: UUID) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_solvers=True))
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        user_db = await self.db_session.get(UserModel, solver_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if user_db in challenge_db.solvers:
            raise mglyph_errors.BadRequestError("User is already a solver of this challenge", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        challenge_db.solvers.append(user_db)
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_db.id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db

    
    async def add_evaluator_to_challenge(self, challenge_id: UUID, evaluator_id: UUID, is_volunteer: bool) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_challenge_evaluator_links=True))
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        user_db = await self.db_session.get(UserModel, evaluator_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        for link in challenge_db.challenge_evaluator_links:
            if link.evaluator_id == evaluator_id:
                # TODO: ? is volunteer_pending and not is_volunteer -> change state to confirmed
                # TODO: ? if invited_pending and is_volunteer -> change state to confirmed
                raise mglyph_errors.BadRequestError("User is already an evaluator of this challenge", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        await self.challenge_evaluator_service.create_challenge_evaluator(challenge_id, evaluator_id, is_volunteer)
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_db.id, load_options=ChallengeRepository.LoadOptions.all_options())
        return challenge_db



def get_challenge_service(
        db_session: SessionDep,
        challenge_repository: ChallengeRepositoryDep,
        evaluation_round_repository: EvaluationRoundRepositoryDep,
        mglyph_evaluation_repository: MGlyphEvaluationRepositoryDep,
        evaluation_round_service: EvaluationRoundServiceDep,
        challenge_evaluator_service: ChallengeEvaluatorServiceDep
    ):
    return ChallengeService(db_session, challenge_repository, evaluation_round_repository, mglyph_evaluation_repository, evaluation_round_service, challenge_evaluator_service)

ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]
