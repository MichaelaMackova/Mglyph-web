from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from db.models.challengeModel import ChallengeModel


class ChallengeCreateDTO(BaseModel):
    name: str
    glyph_submit_deadline: datetime

class SolverDTO(BaseModel):
    id: UUID
    username: str

class ChallengePublicDTO(ChallengeCreateDTO):
    id: UUID
    creation_time: datetime
    submissions_ended: bool
    challenge_finished: bool
    solvers: list[SolverDTO]

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengePublicDTO":
        return ChallengePublicDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            creation_time=challengeModel.creation_time,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline,
            submissions_ended=challengeModel.submissions_ended,
            challenge_finished=challengeModel.challenge_finished,
            solvers=[SolverDTO(id=solver.id, username=solver.username) for solver in challengeModel.solvers]
        )

class ChallengeUpdateDTO(BaseModel):
    name: str | None = None
    glyph_submit_deadline: datetime | None = None
    submissions_ended: bool | None = None
    challenge_finished: bool | None = None
    