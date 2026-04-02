from typing import Annotated
from fastapi import APIRouter, Query, UploadFile, status, Depends
from uuid import UUID
from pathlib import Path
import shutil
from errors import NotFoundError, BadRequestError, ErrorCode
from db.pagination import PagedResponse

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep
from api.mglyph.services import MalleableGlyphServiceDep

from api.mglyph.schemas import MGlyphPublicDTO, MGlyphPublicSimpleDTO, MGlyphCreateDTOAsForm, MglyphFilterParamsAsQuery


router = APIRouter(
    prefix="/mglyph",
    tags=["mglyph"],
)


@router.post("", 
             status_code=status.HTTP_201_CREATED, 
             response_description="Malleable Glyph Created Successfully")
async def create_mglyph(
    mglyph_form: MGlyphCreateDTOAsForm,
    current_user_id: CurrentUserIdDep,
    mglyph_service: MalleableGlyphServiceDep,
    ) -> MGlyphPublicDTO:
    mglyph = await mglyph_service.create_malleable_glyph(mglyph_form, UUID(current_user_id))
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

