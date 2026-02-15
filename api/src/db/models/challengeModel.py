from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime

import db.models.challengeSolverModel as challengeSolverModel
import db.models.challengeEvaluatorModel as challengeEvaluatorModel
import db.models.userModel as userModel



class ChallengeModel(SQLModel, table=True):
    __tablename__ = "challenge"

    __table_args__ = (
        UniqueConstraint("name"),
    )

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str = Field(index=True, unique=True)
    # description: str = Field()
    creation_time: datetime = Field(default_factory=datetime.now)
    glyph_submit_deadline: datetime = Field()
    submissions_ended: bool = Field(default=False)
    challenge_finished: bool = Field(default=False)

    solvers: list["userModel.UserModel"] = Relationship(back_populates="solver_challenges", link_model=challengeSolverModel.ChallengeSolverModel)
    challenge_evaluator_links: list["challengeEvaluatorModel.ChallengeEvaluatorModel"] = Relationship(back_populates="challenge")
