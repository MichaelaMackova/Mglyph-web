from sqlmodel import Field, SQLModel, UniqueConstraint
from uuid import UUID, uuid4

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
    count: int = Field(default=0) #TODO: remove this field, it's only for testing purposes
