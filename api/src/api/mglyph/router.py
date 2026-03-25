from typing import Annotated
from fastapi import APIRouter, Query, UploadFile, status, Depends
from uuid import UUID
from pathlib import Path
import shutil
from pydantic import BaseModel, Json
from errors import NotFoundError, BadRequestError, ErrorCode
from db.pagination import PagedResponse

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep
from api.mglyph.services import MalleableGlyphServiceDep

from api.mglyph.schemas import MGlyphPublicDTO, MGlyphPublicSimpleDTO, MGlyphCreateDTOAsForm, MGlyphCreate, MglyphFilterParamsAsQuery


router = APIRouter(
    prefix="/mglyph",
    tags=["mglyph"],
)


class FormData(BaseModel):
    username: str
    password: str

@router.post("", 
             status_code=status.HTTP_201_CREATED, 
             response_description="Malleable Glyph Created Successfully")
async def create_mglyph(
    mglyph_form: MGlyphCreateDTOAsForm,
    current_user_id: CurrentUserIdDep,
    mglyph_service: MalleableGlyphServiceDep,
    ) -> MGlyphPublicDTO:
    # TODO: Save the uploaded file to a temporary location, do checks, and save to final location
    destination = Path(f"/code/src/{mglyph_form.zip_file.filename}")
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(mglyph_form.zip_file.file, buffer)
    except Exception as e:
        mglyph_form.zip_file.file.close()
        exc = BadRequestError(str(e))
        raise BadRequestError.HTTPException(exc)
    finally:
        mglyph_form.zip_file.file.close()

    mglyph_data = MGlyphCreate.from_dto(mglyph_form, destination.as_posix())
    mglyph = await mglyph_service.create_malleable_glyph(mglyph_data, UUID(current_user_id))
    return MGlyphPublicDTO.from_model(mglyph)



@router.get("")
async def read_malleable_glyphs(
    mglyph_service: MalleableGlyphServiceDep,
    filter_params: MglyphFilterParamsAsQuery,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20
) -> PagedResponse[MGlyphPublicSimpleDTO]:
    paginated_mglyphs = await mglyph_service.get_paginated_malleable_glyphs(filters=filter_params, page=page, size=size)
    paginated_mglyphs.items = [MGlyphPublicSimpleDTO.from_model(mglyph) for mglyph in paginated_mglyphs.items]
    return paginated_mglyphs



@router.get("/{mglyph_id}")
async def read_malleable_glyph(mglyph_id: UUID, mglyph_service: MalleableGlyphServiceDep) -> MGlyphPublicDTO:
    try:
        mglyph = await mglyph_service.get_malleable_glyph_by_id(mglyph_id)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    return MGlyphPublicDTO.from_model(mglyph)




@router.post("/{mglyph_id}/upload-file")
async def upload_mglyph_file(mglyph_id: UUID, file: UploadFile, mglyph_service: MalleableGlyphServiceDep):
    pass

