from sqlmodel import Field, SQLModel, UniqueConstraint
from uuid import UUID, uuid4

class ChallengeSolverModel(SQLModel, table=True):
    __tablename__ = "challenge_solver"
    
    __table_args__ = (
        UniqueConstraint("challenge_id", "solver_id", name="uq_challenge_solver"),
    )

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    challenge_id: UUID = Field(index=True, foreign_key="challenge.id")
    solver_id: UUID = Field(index=True, foreign_key="end_user.id")