from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship, DateTime
from uuid import UUID, uuid4
from datetime import datetime
from utils import get_current_utc_time
from typing import Optional

import db.models.userModel as userModel
import db.models.mglyphEvaluationModel as mglyphEvaluationModel

class MalleableGlyphModel(SQLModel, table=True):
    __tablename__ = "malleable_glyph"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    short_name: str = Field(index=True, max_length=20)
    long_name: str = Field(index=True)
    # description: str = Field()
    last_updated_time: datetime = Field(default_factory=get_current_utc_time, sa_type=DateTime(timezone=True))
    submission_time: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    zip_file_path: str = Field()
    code: str | None = Field(default=None)
    is_code_public: bool = Field(default=False)

    creator_id: UUID = Field(index=True, foreign_key="end_user.id")

    # Relationships
    creator: "userModel.UserModel" = Relationship(back_populates="malleable_glyphs")
    mglyph_evaluation_links: list["mglyphEvaluationModel.MGlyphEvaluationModel"] = Relationship(back_populates="malleable_glyph")