#TODO: odstranit tento model
from datetime import datetime
from sqlmodel import Field, SQLModel

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str = Field(index=True)
    published: bool = Field(default=True)
    created_at: datetime | None = Field(default=datetime.now())