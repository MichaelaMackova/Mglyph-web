from typing import Annotated
from fastapi import APIRouter
from fastapi.responses import FileResponse
from uuid import UUID

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep, CurrentUserIdOrNoneDep
from api.file.services import FileServiceDep


router = APIRouter(
    prefix="/file",
    tags=["file"],
)


@router.get("/{file_id}", response_class=FileResponse)
async def read_file(
    file_id: UUID,
    current_user_id: CurrentUserIdOrNoneDep,
    file_service: FileServiceDep
):
    file_db = await file_service.get_file_by_id(file_id, UUID(current_user_id) if current_user_id else None)
    return FileResponse(path=file_db.path, filename=file_db.filename, media_type=file_db.content_type)

