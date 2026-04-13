from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship, Enum
from uuid import UUID, uuid4
from enum import Enum as PyEnum

import db.models.challengeModel as challengeModel
import db.models.userModel as userModel
import db.models.mglyphEvaluatorModel as mglyphEvaluatorModel

class InvitationType(str, PyEnum):
    volunteer = "volunteer"
    invited = "invited"

class InvitationState(str, PyEnum):
    pending = "pending"
    rejected = "rejected"
    confirmed = "confirmed"


# This is a link table for the many-to-many relationship between ChallengeModel and UserModel, specifically for the evaluators of a challenge
class ChallengeEvaluatorModel(SQLModel, table=True):
    __tablename__ = "challenge_evaluator"

    __table_args__ = (
        UniqueConstraint("challenge_id", "evaluator_id", name= "uq_challenge_evaluator"),
    )
    
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    invitation_state: InvitationState = Field(sa_type=Enum(InvitationState), default=InvitationState.pending)
    invitation_type: InvitationType = Field(sa_type=Enum(InvitationType))
    
    challenge_id: UUID = Field(index=True, foreign_key="challenge.id")
    evaluator_id: UUID = Field(index=True, foreign_key="end_user.id")
    
    #Relationships
    challenge: "challengeModel.ChallengeModel" = Relationship(back_populates="challenge_evaluator_links", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    evaluator: "userModel.UserModel" = Relationship(back_populates="challenge_evaluator_links", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    mglyph_evaluator_links: list["mglyphEvaluatorModel.MGlyphEvaluatorModel"] = Relationship(back_populates="challenge_evaluator", sa_relationship_kwargs=dict(lazy='raise_on_sql'))