from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

import db.models.userModel as userModel

class MalleableGlyphModel(SQLModel, table=True):
    __tablename__ = "malleable_glyph"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    short_name: str = Field(index=True, max_length=20)
    long_name: str = Field(index=True)
    # description: str = Field()
    last_updated_time: datetime = Field(default_factory=datetime.now)
    submission_time: datetime | None = Field(default=None)
    zip_file_path: str = Field()
    code: str | None = Field(default=None)
    is_code_public: bool = Field(default=False)

    creator_id: UUID = Field(index=True, foreign_key="end_user.id")

    # Relationships
    creator: "userModel.UserModel" = Relationship(back_populates="malleable_glyphs")