from fastapi import Depends
from typing import Optional, Annotated
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum

from api.users.schemas import UserPublicSimpleDTO
from api.mglyph.schemas import MGlyphEvaluationPublicDTO

from db.models.challengeModel import ChallengeModel
from db.models.evaluationRoundModel import EvaluationRoundModel



class EvaluationRoundCreateDTO(BaseModel):
    estimated_end_time: datetime

class EvaluationRoundPublicDTO(BaseModel):
    id: UUID
    sequence_number: int
    estimated_end_time: datetime
    creation_time: datetime
    next_round_id: UUID | None

    @staticmethod
    def from_model(evaluationRoundModel: EvaluationRoundModel) -> "EvaluationRoundPublicDTO":
        return EvaluationRoundPublicDTO(
            id=evaluationRoundModel.id,
            sequence_number=evaluationRoundModel.sequence_number,
            estimated_end_time=evaluationRoundModel.estimated_end_time,
            creation_time=evaluationRoundModel.creation_time,
            next_round_id=evaluationRoundModel.next_round_id
        )



class ChallengeFilterParams(BaseModel):
    name_contains: Optional[str] = None
    submissions_ended: Optional[bool] = None
    challenge_finished: Optional[bool] = None

ChallengeFilterParamsAsQuery = Annotated[ChallengeFilterParams, Depends()]


class ChallengeBase(BaseModel):
    name: str
    glyph_submit_deadline: datetime

class ChallengeCreateDTO(ChallengeBase):
    first_evaluation_round: EvaluationRoundCreateDTO
    

class ChallengePublicSimpleDTO(ChallengeBase):
    id: UUID
    submissions_ended: bool
    challenge_finished: bool

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengePublicSimpleDTO":
        return ChallengePublicSimpleDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline,
            submissions_ended=challengeModel.submissions_ended,
            challenge_finished=challengeModel.challenge_finished
        )
    

class ChallengeUserSolverRelationshipType(Enum):
    NONE = "none"
    REGISTERED = "registered"
    MGLYPH_SUBMITTED = "mglyph_submitted"

class ChallengeUserEvaluatorRelationshipType(Enum):
    NONE = "none"
    REGISTERED = "registered"
    EVALUATION_AWAITING = "evaluation_awaiting"
    EVALUATION_FINISHED = "evaluation_finished"

class ChallengeUserRelationshipDTO(BaseModel):
    solver_relationship: ChallengeUserSolverRelationshipType
    evaluator_relationship: ChallengeUserEvaluatorRelationshipType

    @staticmethod
    def from_relationship_flags(is_solver: bool, has_submitted_mglyph: bool, is_evaluator: bool, waiting_for_evaluation: bool) -> "ChallengeUserRelationshipDTO":
        if is_solver:
            if has_submitted_mglyph:
                solver_relationship = ChallengeUserSolverRelationshipType.MGLYPH_SUBMITTED
            else:
                solver_relationship = ChallengeUserSolverRelationshipType.REGISTERED
        else:
            solver_relationship = ChallengeUserSolverRelationshipType.NONE

        if is_evaluator:
            if waiting_for_evaluation:
                evaluator_relationship = ChallengeUserEvaluatorRelationshipType.EVALUATION_AWAITING
            else:
                evaluator_relationship = ChallengeUserEvaluatorRelationshipType.EVALUATION_FINISHED
        else:
            evaluator_relationship = ChallengeUserEvaluatorRelationshipType.NONE

        return ChallengeUserRelationshipDTO(
            solver_relationship=solver_relationship,
            evaluator_relationship=evaluator_relationship
        )

class ChallengePublicMiniDetailDTO(ChallengePublicSimpleDTO):
    mglyph_evaluations: list[MGlyphEvaluationPublicDTO]
    user_relationship: ChallengeUserRelationshipDTO | None


class ChallengePublicDTO(ChallengeBase):
    id: UUID
    creation_time: datetime
    submissions_ended: bool
    challenge_finished: bool
    creator: UserPublicSimpleDTO
    solvers: list[UserPublicSimpleDTO]
    rounds: list[EvaluationRoundPublicDTO]

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengePublicDTO":
        return ChallengePublicDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            creation_time=challengeModel.creation_time,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline,
            submissions_ended=challengeModel.submissions_ended,
            challenge_finished=challengeModel.challenge_finished,
            creator=UserPublicSimpleDTO.from_model(challengeModel.creator),
            solvers=[UserPublicSimpleDTO.from_model(solver) for solver in challengeModel.solvers],
            rounds=[EvaluationRoundPublicDTO.from_model(round) for round in challengeModel.evaluation_rounds]
        )

class ChallengeUpdateDTO(BaseModel):
    name: str | None = None
    glyph_submit_deadline: datetime | None = None
    submissions_ended: bool | None = None
    challenge_finished: bool | None = None
    