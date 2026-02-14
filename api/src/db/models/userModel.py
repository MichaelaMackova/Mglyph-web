from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from datetime import datetime

import db.models.challengeModel as challengeModel
import db.models.challengeSolverModel as challengeSolverModel

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

    solver_challenges: list["challengeModel.ChallengeModel"] = Relationship(back_populates="solvers", link_model=challengeSolverModel.ChallengeSolverModel)
