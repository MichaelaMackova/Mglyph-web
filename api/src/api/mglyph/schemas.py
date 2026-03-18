from fastapi import Form, UploadFile, Depends
from typing import Optional, Annotated
from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime

from api.users.schemas import UserPublicSimpleDTO

from db.models.malleableGlyphModel import MalleableGlyphModel
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel




class MglyphFilterParams(BaseModel):
    short_name_contains: Optional[str] = None
    long_name_contains: Optional[str] = None
    creator_id: Optional[UUID] = None
    is_submitted: Optional[bool] = None

MglyphFilterParamsAsQuery = Annotated[MglyphFilterParams, Depends()]


class MGlyphBase(BaseModel):
    short_name: str
    long_name: str

class MGlyphCreateDTO(MGlyphBase):
    code: Optional[str] = None
    is_code_public: bool
    challenge_id: UUID
    zip_file: UploadFile

    @field_validator("code", mode="before")
    def empty_string_to_none(cls, v):
        """
        Convert empty string from form input to None
        """
        if v in ("", None):
            return None
        return v

MGlyphCreateDTOAsForm = Annotated[MGlyphCreateDTO, Form(media_type= "multipart/form-data")]


class MGlyphCreate(MGlyphBase):
    code: Optional[str] = None
    is_code_public: bool
    challenge_id: UUID
    zip_file_path: str

    @staticmethod
    def from_dto(dto: MGlyphCreateDTO, zip_file_path: str) -> "MGlyphCreate":
        return MGlyphCreate(
            short_name=dto.short_name,
            long_name=dto.long_name,
            code=dto.code,
            is_code_public=dto.is_code_public,
            challenge_id=dto.challenge_id,
            zip_file_path=zip_file_path
        )


class MGlyphPublicSimpleDTO(MGlyphBase):
    id: UUID
    zip_file_path: str # TODO: show only zip_file name or a presigned URL for download instead of the full path
    creator_id: UUID

    @staticmethod
    def from_model(mglyph_model: MalleableGlyphModel) -> "MGlyphPublicSimpleDTO":
        return MGlyphPublicSimpleDTO(
            id=mglyph_model.id,
            short_name=mglyph_model.short_name,
            long_name=mglyph_model.long_name,
            zip_file_path=mglyph_model.zip_file_path, # TODO: show only zip_file name or a presigned URL for download instead of the full path
            creator_id=mglyph_model.creator_id
        )


class MGlyphPublicSimpleWithCreatorDTO(MGlyphBase):
    id: UUID
    zip_file_path: str # TODO: show only zip_file name or a presigned URL for download instead of the full path
    creator: UserPublicSimpleDTO

    @staticmethod
    def from_model(mglyph_model: MalleableGlyphModel) -> "MGlyphPublicSimpleWithCreatorDTO":
        return MGlyphPublicSimpleWithCreatorDTO(
            id=mglyph_model.id,
            short_name=mglyph_model.short_name,
            long_name=mglyph_model.long_name,
            zip_file_path=mglyph_model.zip_file_path, # TODO: show only zip_file name or a presigned URL for download instead of the full path
            creator=UserPublicSimpleDTO.from_model(mglyph_model.creator)
        )


class MGlyphPublicDTO(MGlyphBase):
    id: UUID
    last_updated_time: datetime
    submission_time: datetime | None
    zip_file_path: str # TODO: show only zip_file name or a presigned URL for download instead of the full path
    code: str | None
    is_code_public: bool
    creator: UserPublicSimpleDTO
    # TODO: add evaluations or rank? (and report flags ?)
    #report_flags: list[MGlyphReportFlagPublicDTO]
    #mglyph_evaluations: list[MGlyphEvaluationPublicDTO]

    @staticmethod
    def from_model(mglyph_model: MalleableGlyphModel) -> "MGlyphPublicDTO":
        return MGlyphPublicDTO(
            id=mglyph_model.id,
            short_name=mglyph_model.short_name,
            long_name=mglyph_model.long_name,
            last_updated_time=mglyph_model.last_updated_time,
            submission_time=mglyph_model.submission_time,
            zip_file_path=mglyph_model.zip_file_path, # TODO: show only zip_file name or a presigned URL for download instead of the full path
            code=mglyph_model.code if mglyph_model.is_code_public else None,
            is_code_public=mglyph_model.is_code_public,
            creator=UserPublicSimpleDTO.from_model(mglyph_model.creator)
        )



class MGlyphEvaluationPublicDTO(BaseModel):
    id: UUID
    rank: Optional[int] = None
    score: Optional[float] = None
    malleable_glyph: MGlyphPublicSimpleWithCreatorDTO
    #evaluation_round: EvaluationRoundPublicDTO

    @staticmethod
    def from_model(mglyph_evaluation_model: MGlyphEvaluationModel) -> "MGlyphEvaluationPublicDTO":
        return MGlyphEvaluationPublicDTO(
            id=mglyph_evaluation_model.id,
            rank=mglyph_evaluation_model.rank,
            score=mglyph_evaluation_model.score,
            malleable_glyph=MGlyphPublicSimpleWithCreatorDTO.from_model(mglyph_evaluation_model.malleable_glyph)
            #evaluation_round=EvaluationRoundPublicDTO.from_model(mglyph_evaluation_model.evaluation_round)
        )
