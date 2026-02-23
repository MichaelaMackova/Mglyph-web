from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

import db.models.malleableGlyphModel as malleableGlyphModel
import db.models.evaluationRoundModel as evaluationRoundModel
import db.models.mglyphEvaluatorModel as mglyphEvaluatorModel


class MGlyphEvaluationModel(SQLModel, table=True):
    __tablename__ = "mglyph_evaluation"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    rank: int | None = Field(default=None) # The rank of the malleable glyph in the evaluation round, starting from 1. Can be null if the evaluation round is not finished yet.
    score: float | None = Field(default=None)

    malleable_glyph_id: UUID = Field(index=True, foreign_key="malleable_glyph.id")
    evaluation_round_id: UUID = Field(index=True, foreign_key="evaluation_round.id")

    # Relationships
    malleable_glyph: "malleableGlyphModel.MalleableGlyphModel" = Relationship(back_populates="mglyph_evaluation_links", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    evaluation_round: "evaluationRoundModel.EvaluationRoundModel" = Relationship(back_populates="mglyph_evaluation_links", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    mglyph_evaluator_links: list["mglyphEvaluatorModel.MGlyphEvaluatorModel"] = Relationship(back_populates="mglyph_evaluation", sa_relationship_kwargs=dict(lazy='raise_on_sql'))