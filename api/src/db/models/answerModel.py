from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional

import db.models.mglyphEvaluatorModel as mglyphEvaluatorModel


class AnswerModel(SQLModel, table=True):
    __tablename__ = "answer"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    first_glyph_value: float = Field()
    second_glyph_value: float = Field()
    answered_symbol: str = Field(max_length=1)
    is_answer_correct: bool = Field()
    glyph_distance: float = Field()
    answer_time: datetime = Field(default_factory=datetime.now)
    time_taken: timedelta = Field()
    rotation_type: Optional[str] = Field(default=None)
    first_glyph_rotation_angle: float = Field(default=0.0)
    second_glyph_rotation_angle: float = Field(default=0.0)

    mglyph_evaluator_id: UUID = Field(index=True, foreign_key="mglyph_evaluator.id")

    # Relationships
    mglyph_evaluator_link: "mglyphEvaluatorModel.MGlyphEvaluatorModel" = Relationship(back_populates="answers", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
