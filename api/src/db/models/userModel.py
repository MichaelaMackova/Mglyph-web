from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime

import db.models.challengeEvaluatorModel as challengeEvaluatorModel
import db.models.challengeModel as challengeModel
import db.models.challengeSolverModel as challengeSolverModel
import db.models.malleableGlyphModel as malleableGlyphModel
import db.models.mglyphReportFlagModel as mglyphReportFlagModel

class UserModel(SQLModel, table=True):
    __tablename__ = "end_user" # "user" is a reserved keyword, so we use "end_user" instead

    __table_args__ = (
        UniqueConstraint("username"),
        UniqueConstraint("email"),
        UniqueConstraint("google_sub"),
    )

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    username: str = Field(index=True, unique=True)
    role: str = Field(default="user") # Possible values: "user", "admin"
    email: str = Field(index=True, unique=True)
    google_sub: str | None = Field(index=True, unique=True)
    # creation_time: datetime = Field(default_factory=datetime.now) # TODO: add
    count: int = Field(default=0) #TODO: remove this field, it's only for testing purposes

    # Relationships
    solver_challenges: list["challengeModel.ChallengeModel"] = Relationship(back_populates="solvers", link_model=challengeSolverModel.ChallengeSolverModel, sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    challenge_evaluator_links: list["challengeEvaluatorModel.ChallengeEvaluatorModel"] = Relationship(back_populates="evaluator", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    malleable_glyphs: list["malleableGlyphModel.MalleableGlyphModel"] = Relationship(back_populates="creator", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    created_challenges: list["challengeModel.ChallengeModel"] = Relationship(back_populates="creator", sa_relationship_kwargs=dict(lazy='raise_on_sql'))
    reported_flags: list["mglyphReportFlagModel.MGlyphReportFlagModel"] = Relationship(back_populates="user_reporter", sa_relationship_kwargs=dict(foreign_keys="mglyphReportFlagModel.MGlyphReportFlagModel.user_reporter_id", lazy='raise_on_sql'))
    resolved_flags: list["mglyphReportFlagModel.MGlyphReportFlagModel"] = Relationship(back_populates="user_resolver", sa_relationship_kwargs=dict(foreign_keys="mglyphReportFlagModel.MGlyphReportFlagModel.user_resolver_id", lazy='raise_on_sql'))
