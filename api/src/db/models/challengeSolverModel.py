from sqlmodel import Field, SQLModel, UniqueConstraint
from uuid import UUID, uuid4

# This is a link table for the many-to-many relationship between ChallengeModel and UserModel
class ChallengeSolverModel(SQLModel, table=True):
    __tablename__ = "challenge_solver"
    
    challenge_id: UUID = Field(index=True, foreign_key="challenge.id", primary_key=True)
    solver_id: UUID = Field(index=True, foreign_key="end_user.id", primary_key=True)
    