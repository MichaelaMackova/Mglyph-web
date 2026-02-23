from typing import Annotated

from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from settings import ASYNC_DB_URI, SYNC_DB_URI

engine = create_async_engine(ASYNC_DB_URI)


SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



def create_db_and_tables():
    # from .models import posts, heroModel  # NOTE: Import models here to register them with SQLModel
    import db.models  # Ensure all models are imported
    engine_sync = create_engine(SYNC_DB_URI)
    SQLModel.metadata.create_all(engine_sync)



async def get_session():
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]