from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4

class UserModel(SQLModel, table=True):
    __tablename__ = "user"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    email: str = Field(index=True, unique=True)
    google_sub: str | None = Field(index=True, unique=True)
    count: int = Field(default=0)