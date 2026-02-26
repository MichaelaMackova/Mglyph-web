from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from api.users.schemas import UserPublicSimpleDTO

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
    