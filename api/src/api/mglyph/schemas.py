from fastapi import Form, UploadFile, Depends
from typing import Optional, Annotated
from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime

from api.users.schemas import UserPublicSimpleDTO
from api.challenges.challenge_state_schema import ChallengeState

from db.models.malleableGlyphModel import MalleableGlyphModel
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.challengeModel import ChallengeModel



class MglyphFilterParams(BaseModel):
    short_name_contains: Optional[str] = None
    long_name_contains: Optional[str] = None
    creator_id: Optional[UUID] = None

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



class MGlyphPublicSimpleDTO(MGlyphBase):
    id: UUID
    zip_file_id: UUID
    creator_id: UUID

    @staticmethod
    def from_model(mglyph_model: MalleableGlyphModel) -> "MGlyphPublicSimpleDTO":
        return MGlyphPublicSimpleDTO(
            id=mglyph_model.id,
            short_name=mglyph_model.short_name,
            long_name=mglyph_model.long_name,
            zip_file_id=mglyph_model.zip_file_id,
            creator_id=mglyph_model.creator_id
        )


class MGlyphPublicSimpleWithCreatorDTO(MGlyphBase):
    id: UUID
    zip_file_id: UUID
    creator: UserPublicSimpleDTO

    @staticmethod
    def from_model(mglyph_model: MalleableGlyphModel) -> "MGlyphPublicSimpleWithCreatorDTO":
        return MGlyphPublicSimpleWithCreatorDTO(
            id=mglyph_model.id,
            short_name=mglyph_model.short_name,
            long_name=mglyph_model.long_name,
            zip_file_id=mglyph_model.zip_file_id,
            creator=UserPublicSimpleDTO.from_model(mglyph_model.creator)
        )



class MGlyphEvaluationPublicSimpleDTO(BaseModel):
    id: UUID
    rank: Optional[int] = None
    score: Optional[float] = None

    @staticmethod
    def from_model(mglyph_evaluation_model: MGlyphEvaluationModel) -> "MGlyphEvaluationPublicSimpleDTO":
        return MGlyphEvaluationPublicSimpleDTO(
            id=mglyph_evaluation_model.id,
            rank=mglyph_evaluation_model.rank,
            score=mglyph_evaluation_model.score
        )

class ChallengeSimpleDTO(BaseModel):
    id: UUID
    name: str
    state: ChallengeState

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengeSimpleDTO":
        return ChallengeSimpleDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            state=ChallengeState.from_model_params(challengeModel.challenge_finished, challengeModel.submissions_ended),
        )


class MGlyphPublicDTO(MGlyphBase):
    id: UUID
    last_updated_time: datetime
    submission_time: datetime | None
    zip_file_id: UUID
    code: str | None
    is_code_public: bool
    creator: UserPublicSimpleDTO
    challenge: ChallengeSimpleDTO
    last_evaluation: MGlyphEvaluationPublicSimpleDTO
    # EXTENSION: report_flags: list[MGlyphReportFlagPublicDTO]

    @staticmethod
    def from_model(mglyph_model: MalleableGlyphModel) -> "MGlyphPublicDTO":
        last_mglyph_evaluation = mglyph_model.mglyph_evaluation_links[-1]
        if last_mglyph_evaluation.evaluation_round.next_round_id is not None:
            for mglyph_evaluation in mglyph_model.mglyph_evaluation_links:
                if mglyph_evaluation.evaluation_round.sequence_number > last_mglyph_evaluation.evaluation_round.sequence_number:
                    last_mglyph_evaluation = mglyph_evaluation
        return MGlyphPublicDTO(
            id=mglyph_model.id,
            short_name=mglyph_model.short_name,
            long_name=mglyph_model.long_name,
            last_updated_time=mglyph_model.last_updated_time,
            submission_time=mglyph_model.submission_time,
            zip_file_id=mglyph_model.zip_file_id,
            code=mglyph_model.code if mglyph_model.is_code_public else None,
            is_code_public=mglyph_model.is_code_public,
            creator=UserPublicSimpleDTO.from_model(mglyph_model.creator),
            challenge=ChallengeSimpleDTO.from_model(last_mglyph_evaluation.evaluation_round.challenge),
            last_evaluation=MGlyphEvaluationPublicSimpleDTO.from_model(last_mglyph_evaluation)
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
