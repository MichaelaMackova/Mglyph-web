from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

import db.models.mglyphEvaluationModel as mglyphEvaluationModel
import db.models.challengeEvaluatorModel as challengeEvaluatorModel

class MGlyphEvaluatorModel(SQLModel, table=True):
    __tablename__ = "mglyph_evaluator"

    __table_args__ = (
        UniqueConstraint("mglyph_evaluation_id", "challenge_evaluator_id", name="uq_challenge_mglyph_evaluator"),
    )

    id: UUID = Field(primary_key=True, default_factory=uuid4)

    mglyph_evaluation_id: UUID = Field(index=True, foreign_key="mglyph_evaluation.id")
    challenge_evaluator_id: UUID = Field(index=True, foreign_key="challenge_evaluator.id")

    # Relationships
    mglyph_evaluation: "mglyphEvaluationModel.MGlyphEvaluationModel" = Relationship(back_populates="mglyph_evaluator_links")
    challenge_evaluator: "challengeEvaluatorModel.ChallengeEvaluatorModel" = Relationship(back_populates="mglyph_evaluator_links")