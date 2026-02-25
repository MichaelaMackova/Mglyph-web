from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship, DateTime
from uuid import UUID, uuid4
from datetime import datetime
from utils import get_current_utc_time

import db.models.challengeSolverModel as challengeSolverModel
import db.models.challengeEvaluatorModel as challengeEvaluatorModel
import db.models.evaluationRoundModel as evaluationRoundModel
import db.models.userModel as userModel



class ChallengeModel(SQLModel, table=True):
    __tablename__ = "challenge"

    __table_args__ = (
        UniqueConstraint("name"),
    )

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str = Field(index=True, unique=True)
    # description: str = Field()
    creation_time: datetime = Field(default_factory=get_current_utc_time, sa_type=DateTime(timezone=True))
    glyph_submit_deadline: datetime = Field(sa_type=DateTime(timezone=True))
    submissions_ended: bool = Field(default=False)
    challenge_finished: bool = Field(default=False)

    creator_id: UUID = Field(foreign_key="end_user.id")

    # Relationships
    creator: "userModel.UserModel" = Relationship(back_populates="created_challenges", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    solvers: list["userModel.UserModel"] = Relationship(back_populates="solver_challenges", link_model=challengeSolverModel.ChallengeSolverModel, sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    challenge_evaluator_links: list["challengeEvaluatorModel.ChallengeEvaluatorModel"] = Relationship(back_populates="challenge", cascade_delete=True, sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    evaluation_rounds: list["evaluationRoundModel.EvaluationRoundModel"] = Relationship(back_populates="challenge", cascade_delete=True, sa_relationship_kwargs=dict(lazy='raise_on_sql'))
