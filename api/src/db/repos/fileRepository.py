from typing import Annotated
from fastapi import Depends
from db.database import SessionDep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import Select
from uuid import UUID
from db.repos.interface import RepositoryInterface

from db.models.fileModel import FileModel



class FileRepository(RepositoryInterface):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    class LoadOptions(RepositoryInterface.LoadOptionsInterface):
        def __init__(self, load_malleable_glyph: bool = False):
            self.load_malleable_glyph = load_malleable_glyph

        @staticmethod
        def all_options():
            return FileRepository.LoadOptions(load_malleable_glyph=True)

        def add_options_to_statement(self, statement: Select) -> Select:
            if self.load_malleable_glyph:
                statement = statement.options(joinedload(FileModel.malleable_glyph))
            return statement
        
    async def get_file_by_id(self, file_id: UUID, load_options: LoadOptions = LoadOptions()) -> FileModel | None:
        statement = select(FileModel).where(FileModel.id == file_id)
        statement = load_options.add_options_to_statement(statement)
        result = await self.db_session.execute(statement)
        return result.scalar_one_or_none()
    


def get_file_repository(db_session: SessionDep) -> FileRepository:
    return FileRepository(db_session)

FileRepositoryDep = Annotated[FileRepository, Depends(get_file_repository)]