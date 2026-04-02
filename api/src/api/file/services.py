from typing import Annotated
from fastapi import Depends, UploadFile
from pathlib import Path
import shutil
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import SessionDep
from uuid import UUID, uuid4
import errors as mglyph_errors
from data import DATA_PATH
import os
# Models
from db.models.fileModel import FileModel
# Dependencies
from db.repos.fileRepository import FileRepository, FileRepositoryDep




class FileService:
    def __init__(self, db_session: AsyncSession, file_repository: FileRepository):
        self.db_session = db_session
        self.file_repository = file_repository

    def __generate_unique_filename(self, save_dir: Path, file_extension: str, file_prefix: str | None = None, file_suffix: str | None = None, return_path: bool = False) -> str:
        """
        Generates a unique filename in the specified directory with the given extension, prefix, and suffix.
        Ensures that the generated filename does not already exist in the directory.

        Args:
            save_dir (Path): The existing directory where the file will be saved.
            file_extension (str): The extension for the new file (e.g., "txt", "pdf", "zip").
            file_prefix (str | None): A prefix for the filename.
            file_suffix (str | None): A suffix for the filename.
            return_path (bool): If True, returns the full path of the generated file. If False, returns just the filename.

        Returns:
            str: Unique filename (or full path) with the specified extension, prefix, and suffix that does not exist in the save_dir. Generates filenames in the format: {file_prefix}{unique_id}{file_suffix}.{file_extension}
        """
        if not save_dir.is_dir():
            mglyph_errors.ServerError("Save directory does not exist", error_code=mglyph_errors.ErrorCode.SERVER_ERROR_FILE_SAVE_FAILED)
            
        if file_prefix is None:
            file_prefix = ""
        if file_suffix is None:
            file_suffix = ""

        while True:
            fileName = file_prefix + uuid4().hex + file_suffix + '.' + file_extension
            newFilePath = os.path.join(save_dir, fileName)
            if not os.path.exists(newFilePath):
                break
        
        if return_path:
            return newFilePath
        return fileName


    async def create_mglyph_file(self, upload_file: UploadFile, commit: bool = True) -> FileModel:
        # TODO: Save the uploaded file to a temporary location, do checks, and save to final location
        original_filename = upload_file.filename
        destination_dir = Path(os.path.join(DATA_PATH, "files"))
        if not destination_dir.is_dir():
            destination_dir.mkdir(parents=True, exist_ok=True)
        destination = Path(self.__generate_unique_filename(destination_dir, file_extension="zip", return_path=True))
        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        except Exception as e:
            upload_file.file.close()
            raise mglyph_errors.MGlyphApiError(str(e))
        finally:
            upload_file.file.close()

        file_db = FileModel(
            id=None,
            filename=original_filename,
            content_type="application/zip",
            path=destination.as_posix()
        )
        self.db_session.add(file_db)
        if commit:
            await self.db_session.commit()
        else:
            await self.db_session.flush()  # Flush to get the ID without committing
        await self.db_session.refresh(file_db)
        return file_db
    
    async def get_file_by_id(self, file_id: UUID, current_user_id: UUID | None) -> FileModel:
        file_db = await self.file_repository.get_file_by_id(file_id, load_options=FileRepository.LoadOptions(load_malleable_glyph=True))
        if not file_db:
            raise mglyph_errors.NotFoundError("File with given ID")
        if file_db.malleable_glyph.submission_time is None and file_db.malleable_glyph.creator_id != current_user_id:
            raise mglyph_errors.ForbiddenError("You do not have permission to access this file")
        if not Path(file_db.path).is_file():
            raise mglyph_errors.NotFoundError("File on disk")
        return file_db


def get_file_service(db_session: SessionDep, file_repository: FileRepositoryDep) -> FileService:
    return FileService(db_session, file_repository)

FileServiceDep = Annotated[FileService, Depends(get_file_service)]