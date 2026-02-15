from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4

import db.models.challengeModel as challengeModel
import db.models.userModel as userModel


# This is a link table for the many-to-many relationship between ChallengeModel and UserModel, specifically for the evaluators of a challenge
class ChallengeEvaluatorModel(SQLModel, table=True):
    __tablename__ = "challenge_evaluator"

    __table_args__ = (
        UniqueConstraint("challenge_id", "evaluator_id", name= "uq_challenge_evaluator"),
    )
    
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    challenge_id: UUID = Field(index=True, foreign_key="challenge.id")
    evaluator_id: UUID = Field(index=True, foreign_key="end_user.id")
    
    challenge: "challengeModel.ChallengeModel" = Relationship(back_populates="challenge_evaluator_links")
    evaluator: "userModel.UserModel" = Relationship(back_populates="challenge_evaluator_links")