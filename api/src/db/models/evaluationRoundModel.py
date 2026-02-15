from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

import db.models.challengeModel as challengeModel


class EvaluationRoundModel(SQLModel, table=True):
    __tablename__ = "evaluation_round"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    sequence_number: int = Field() # The sequence number of the evaluation round for a specific challenge, starting from 1
    estimated_end_time: datetime = Field()
    creation_time: datetime = Field(default_factory=datetime.now)

    challenge_id: UUID = Field(index=True, foreign_key="challenge.id")
    next_round_id: UUID | None = Field(foreign_key="evaluation_round.id", default=None)

    # Relationships
    challenge: "challengeModel.ChallengeModel" = Relationship(back_populates="evaluation_rounds")
    next_round: Optional["EvaluationRoundModel"] = Relationship(back_populates="previous_round", sa_relationship_kwargs=dict(remote_side="EvaluationRoundModel.id")) #, sa_relationship_kwargs={"uselist": False})
    previous_round:  Optional["EvaluationRoundModel"] = Relationship(back_populates="next_round") #, sa_relationship_kwargs={"uselist": False})
