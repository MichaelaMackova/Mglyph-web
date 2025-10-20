from typing import Annotated

from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine

from settings import DB_URI

engine = create_engine(DB_URI)



def create_db_and_tables():
    # from .models import posts, heroModel  # NOTE: Import models here to register them with SQLModel
    import db.models  # Ensure all models are imported
    SQLModel.metadata.create_all(engine)



def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]