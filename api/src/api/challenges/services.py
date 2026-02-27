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

from db.repos.challengeRepository import ChallengeRepository, ChallengeRepositoryDep
from db.repos.evaluationRoundRepository import EvaluationRoundRepository, EvaluationRoundRepositoryDep

from api.challenges.schemas import ChallengePublicDTO, ChallengeCreateDTO, ChallengeUpdateDTO


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





# TODO: přidat kontroly:
#           - challenge creation_time < glyph_submit_deadline < first evaluation round estimated_end_time
#           - při přidávání solvera zkontrolovat, že nejsou uzavřené submissiony
#           - při updatu zkontrolovat, že nenastane stav (submissions_ended = False and challenge_finished = True)
#           - při updatu zkontrolovat, že se nemění submissions_ended nebo challenge_finished z True na False

class ChallengeService:
    def __init__(self, db_session: AsyncSession, challenge_repository: ChallengeRepository, evaluation_round_repository: EvaluationRoundRepository, evaluation_round_service: EvaluationRoundService):
        self.db_session = db_session
        self.challenge_repository = challenge_repository
        self.evaluation_round_repository = evaluation_round_repository
        self.evaluation_round_service = evaluation_round_service


    async def get_challenge_by_id(self, challenge_id: UUID) -> ChallengeModel:
        db_challenge = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        if not db_challenge:
            raise mglyph_errors.NotFoundError("Challenge")
        return db_challenge


    async def get_paginated_challenges(self, offset: int = 0, limit: int = 100) -> list[ChallengeModel]:
        challenges_db = await self.challenge_repository.get_paginated_challenges(offset=offset, limit=limit)
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
            raise mglyph_errors.NotFoundError("Challenge")
        challenge_data = challenge_update.model_dump(exclude_unset=True)
        challenge_db.sqlmodel_update(challenge_data)
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db
    

    async def delete_challenge(self, challenge_id: UUID):
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge")
        first_round = await self.evaluation_round_repository.get_first_round_in_challenge(challenge_id, load_options=EvaluationRoundRepository.LoadOptions(load_mglyph_evaluation_links=True))
        if first_round:
            if first_round.mglyph_evaluation_links:
                raise mglyph_errors.BadRequestError("Cannot delete challenge with existing assigned malleable glyphs")
        await self.db_session.delete(challenge_db)
        await self.db_session.commit()
    

    async def add_solver_to_challenge(self, challenge_id: UUID, solver_id: UUID) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_solvers=True))
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge")
        user_db = await self.db_session.get(UserModel, solver_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User")
        if user_db in challenge_db.solvers:
            raise mglyph_errors.BadRequestError("User is already a solver of this challenge")
        challenge_db.solvers.append(user_db)
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_db.id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db



def get_challenge_service(db_session: SessionDep, challenge_repository: ChallengeRepositoryDep, evaluation_round_repository: EvaluationRoundRepositoryDep, evaluation_round_service: EvaluationRoundServiceDep):
    return ChallengeService(db_session, challenge_repository, evaluation_round_repository, evaluation_round_service)

ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]
