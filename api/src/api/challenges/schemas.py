from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from api.auth.schemas import UserPublicSimpleDTO

from db.models.challengeModel import ChallengeModel


class ChallengeCreateDTO(BaseModel):
    name: str
    glyph_submit_deadline: datetime

class ChallengePublicSimpleDTO(ChallengeCreateDTO):
    id: UUID

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengePublicSimpleDTO":
        return ChallengePublicSimpleDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline
        )

class ChallengePublicDTO(ChallengeCreateDTO):
    id: UUID
    creation_time: datetime
    submissions_ended: bool
    challenge_finished: bool
    solvers: list[UserPublicSimpleDTO]

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengePublicDTO":
        return ChallengePublicDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            creation_time=challengeModel.creation_time,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline,
            submissions_ended=challengeModel.submissions_ended,
            challenge_finished=challengeModel.challenge_finished,
            solvers=[UserPublicSimpleDTO.from_model(solver) for solver in challengeModel.solvers]
        )

class ChallengeUpdateDTO(BaseModel):
    name: str | None = None
    glyph_submit_deadline: datetime | None = None
    submissions_ended: bool | None = None
    challenge_finished: bool | None = None
    