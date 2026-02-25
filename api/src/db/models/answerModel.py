from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship, DateTime, Column, Enum
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional
from utils import get_current_utc_time
from enum import Enum as PyEnum

import db.models.mglyphEvaluatorModel as mglyphEvaluatorModel


class AnsweredSymbol(str, PyEnum):
    greater = "greater"
    less = "less"
    equal = "equal"


class RotationType(str, PyEnum):
    same = "same"
    different = "different"


class AnswerModel(SQLModel, table=True):
    __tablename__ = "answer"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    first_glyph_value: float = Field()
    second_glyph_value: float = Field()
    answered_symbol: AnsweredSymbol = Field(sa_type=Enum(AnsweredSymbol))
    is_answer_correct: bool = Field()
    glyph_distance: float = Field()
    answer_time: datetime = Field(default_factory=get_current_utc_time, sa_type=DateTime(timezone=True))
    time_taken: timedelta = Field()
    rotation_type: Optional[RotationType] = Field(default=None, sa_type=Enum(RotationType))
    first_glyph_rotation_angle: float = Field(default=0.0)
    second_glyph_rotation_angle: float = Field(default=0.0)

    mglyph_evaluator_id: UUID = Field(index=True, foreign_key="mglyph_evaluator.id")

    # Relationships
    mglyph_evaluator_link: "mglyphEvaluatorModel.MGlyphEvaluatorModel" = Relationship(back_populates="answers", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
