from typing import Annotated
from fastapi import Depends, status
from pydantic import ValidationError
from sqlmodel import select, Session
from db.database import SessionDep
from uuid import UUID
from datetime import datetime, timedelta
import errors as mglyph_errors

from db.models.challengeModel import ChallengeModel
from db.models.userModel import UserModel
from db.models.evaluationRoundModel import EvaluationRoundModel

from api.challenges.schemas import ChallengePublicDTO, ChallengeCreateDTO, ChallengeUpdateDTO


class EvaluationRoundService:
    def __init__(self, db_session: Session):
        self.db_session = db_session



    def create_initial_evaluation_round(self, challenge_id: UUID) -> EvaluationRoundModel:
        evaluation_round = EvaluationRoundModel(
            id=None,
            sequence_number=1,
            estimated_end_time=datetime.now() + timedelta(days=7),  # Example: set estimated end time to 7 days from now ; TODO: make it configurable (add to challengeCreateDTO)
            challenge_id=challenge_id,
            name="Initial Evaluation Round",
            description="This is the initial evaluation round for the challenge.",
            is_active=True
        )
        self.db_session.add(evaluation_round)
        self.db_session.commit()
        self.db_session.refresh(evaluation_round)
        return evaluation_round


def get_evaluation_round_service(db_session: SessionDep):
    return EvaluationRoundService(db_session)

EvaluationRoundServiceDep = Annotated[EvaluationRoundService, Depends(get_evaluation_round_service)]






class ChallengeService:
    def __init__(self, db_session: Session, evaluation_round_service: EvaluationRoundService):
        self.db_session = db_session
        self.evaluation_round_service = evaluation_round_service


    def __get_challenge_db(self, challenge_id: UUID) -> ChallengeModel:
        challenge_db = self.db_session.get(ChallengeModel, challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge")
        return challenge_db



    def get_challenge_by_id(self, challenge_id: UUID) -> ChallengeModel:
        return self.__get_challenge_db(challenge_id)
    


    def get_all_challenges(self, offset: int = 0, limit: int = 100) -> list[ChallengeModel]:
        challenges_db = self.db_session.exec(select(ChallengeModel).offset(offset).limit(limit)).all()
        return challenges_db
    


    def create_challenge(self, challenge: ChallengeCreateDTO, current_user_id: UUID) -> ChallengeModel:
        try:
            challenge_data = challenge.model_dump()
            challenge_data["creator_id"] = current_user_id
            db_challenge = ChallengeModel.model_validate(challenge_data)
            db_challenge.id = None  # Ensure ID is None for new records
        except ValidationError as e:
            pass # TODO: raise exception
        self.db_session.add(db_challenge)
        self.db_session.commit()
        self.db_session.refresh(db_challenge)

        # Add first evaluation round
        self.evaluation_round_service.create_initial_evaluation_round(db_challenge.id)
        self.db_session.refresh(db_challenge)
        return db_challenge
    


    def update_challenge(self, challenge_id: UUID, challenge_update: ChallengeUpdateDTO) -> ChallengeModel:
        challenge_db = self.__get_challenge_db(challenge_id)
        challenge_data = challenge_update.model_dump(exclude_unset=True)
        challenge_db.sqlmodel_update(challenge_data)
        self.db_session.add(challenge_db)
        self.db_session.commit()
        self.db_session.refresh(challenge_db)
        return challenge_db
    


    def delete_challenge(self, challenge_id: UUID):
        challenge_db = self.db_session.get(ChallengeModel, challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge")
        self.db_session.delete(challenge_db)
        self.db_session.commit()
    


    def add_solver_to_challenge(self, challenge_id: UUID, solver_id: UUID) -> ChallengeModel:
        challenge_db = self.__get_challenge_db(challenge_id)
        user_db = self.db_session.get(UserModel, solver_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User")
        challenge_db.solvers.append(user_db)
        self.db_session.add(challenge_db)
        self.db_session.commit()
        self.db_session.refresh(challenge_db)
        return challenge_db



def get_challenge_service(db_session: SessionDep, evaluation_round_service: EvaluationRoundServiceDep):
    return ChallengeService(db_session, evaluation_round_service)

ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]
