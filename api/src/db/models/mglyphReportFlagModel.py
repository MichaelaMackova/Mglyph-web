from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship, DateTime
from uuid import UUID, uuid4
from datetime import datetime
from utils import get_current_utc_time
from typing import Optional

import db.models.userModel as userModel


class MGlyphReportFlagModel(SQLModel, table=True):
    __tablename__ = "mglyph_report_flag"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    flag_type: str = Field()
    comment: Optional[str] = Field(default=None)
    creation_time: datetime = Field(default_factory=get_current_utc_time, sa_type=DateTime(timezone=True))
    status: str = Field(default="open") # Possible values: "open", "closed"
    last_updated_time: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    history: str = Field() # A string that keeps track of the history of the flag, e.g. when it was created, when it was closed, etc.

    user_reporter_id: UUID = Field(foreign_key="end_user.id")
    user_resolver_id: Optional[UUID] = Field(default=None, foreign_key="end_user.id")

    # Relationships
    user_reporter: "userModel.UserModel" = Relationship(back_populates="reported_flags", sa_relationship_kwargs=dict(foreign_keys="MGlyphReportFlagModel.user_reporter_id", lazy='raise_on_sql'))
    user_resolver: Optional["userModel.UserModel"] = Relationship(back_populates="resolved_flags", sa_relationship_kwargs=dict(foreign_keys="MGlyphReportFlagModel.user_resolver_id", lazy='raise_on_sql'))
