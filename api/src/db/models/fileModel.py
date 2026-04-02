from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship, DateTime, Enum
from uuid import UUID, uuid4
from datetime import datetime
from utils import get_current_utc_time

import db.models.malleableGlyphModel as malleableGlyphModel

class FileModel(SQLModel, table=True):
    __tablename__ = "file"

    __table_args__ = (
        UniqueConstraint("path"),
    )

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    filename: str = Field()
    content_type: str = Field()
    path: str = Field(unique=True)

    # Relationships
    malleable_glyph: "malleableGlyphModel.MalleableGlyphModel" = Relationship(back_populates="zip_file", sa_relationship_kwargs=dict(lazy='raise_on_sql'))