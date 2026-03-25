from typing import Annotated
from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import SessionDep
from uuid import UUID
from datetime import datetime
import errors as mglyph_errors
from db.pagination import PagedResponse
# Models
from db.models.malleableGlyphModel import MalleableGlyphModel
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
# Dependencies
from db.repos.malleableGlyphRepository import MalleableGlyphRepository, MalleableGlyphRepositoryDep
from db.repos.evaluationRoundRepository import EvaluationRoundRepository, EvaluationRoundRepositoryDep
from db.repos.challengeRepository import ChallengeRepository, ChallengeRepositoryDep
# Schemas
from api.mglyph.schemas import MGlyphCreate, MglyphFilterParams




class MGlyphEvaluationService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_evaluation_for_mglyph(self, mglyph_id: UUID, evaluation_round_id: UUID) -> MGlyphEvaluationModel:
        mglyph_evaluation = MGlyphEvaluationModel(
            id=None,
            rank=None,
            score=None,
            malleable_glyph_id=mglyph_id,
            evaluation_round_id=evaluation_round_id
        )
        self.db_session.add(mglyph_evaluation)
        await self.db_session.commit()
        await self.db_session.refresh(mglyph_evaluation)
        return mglyph_evaluation


def get_mglyph_evaluation_service(db_session: SessionDep):
    return MGlyphEvaluationService(db_session)

MGlyphEvaluationServiceDep = Annotated[MGlyphEvaluationService, Depends(get_mglyph_evaluation_service)]




class MalleableGlyphService:
    def __init__(
            self,
            db_session: AsyncSession,
            malleable_glyph_repository: MalleableGlyphRepository,
            evaluation_round_repository: EvaluationRoundRepository,
            challenge_repository: ChallengeRepository,
            mglyph_evaluation_service: MGlyphEvaluationService
            ):
        self.db_session = db_session
        self.malleable_glyph_repository = malleable_glyph_repository
        self.evaluation_round_repository = evaluation_round_repository
        self.challenge_repository = challenge_repository
        self.mglyph_evaluation_service = mglyph_evaluation_service


    async def get_malleable_glyph_by_id(self, mglyph_id: UUID) -> MalleableGlyphModel:
        db_mglyph = await self.malleable_glyph_repository.get_malleable_glyph_by_id(mglyph_id, load_options=MalleableGlyphRepository.LoadOptions.all_options())
        if not db_mglyph:
            raise mglyph_errors.NotFoundError("Malleable Glyph", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        return db_mglyph

    
    async def get_paginated_malleable_glyphs(self, filters: MglyphFilterParams, page: int = 1, size: int = 20) -> PagedResponse[MalleableGlyphModel]:
        filter_params = MalleableGlyphRepository.FilterParams(
            short_name_contains=filters.short_name_contains,
            long_name_contains=filters.long_name_contains,
            creator_id=filters.creator_id,
            is_submitted=filters.is_submitted
        )
        paginated_mglyphs_db = await self.malleable_glyph_repository.get_paginated_malleable_glyphs(filters=filter_params, page=page, size=size)
        return paginated_mglyphs_db
    

    async def create_malleable_glyph(self, mglyph_create_dto: MGlyphCreate, current_user_id: UUID) -> MalleableGlyphModel:
        try: 
            mglyph_data = mglyph_create_dto.model_dump()
            mglyph_data["creator_id"] = current_user_id
            challenge_id = mglyph_data.pop("challenge_id")
            db_mglyph = MalleableGlyphModel.model_validate(mglyph_data)
            db_mglyph.id = None  # Ensure ID is None for new records
        except ValidationError as e:
            raise mglyph_errors.BadRequestError(f"Invalid malleable glyph data: {e}")
        
        db_challenge = await self.challenge_repository.get_challenge_by_id(mglyph_create_dto.challenge_id, load_options=ChallengeRepository.LoadOptions(load_solvers=True))
        if not db_challenge:
            raise mglyph_errors.BadRequestError("Challenge with given ID does not exist")# TODO: mglyph_errors.ErrorCode.BAD_REQUEST_INVALID_REFERENCE)
        if not db_challenge.solvers or (db_challenge.solvers and current_user_id not in [solver.id for solver in db_challenge.solvers]):
            raise mglyph_errors.BadRequestError("User is not a solver in the specified challenge")# TODO: mglyph_errors.ErrorCode.BAD_REQUEST_INVALID_REFERENCE)
        if db_challenge.submissions_ended:
            raise mglyph_errors.BadRequestError("Submissions for this challenge have ended")# TODO: mglyph_errors.ErrorCode.BAD_REQUEST_INVALID_STATE)

        db_first_eval_round = await self.evaluation_round_repository.get_first_round_in_challenge(challenge_id)  # Check if challenge has at least one evaluation round
        if not db_first_eval_round:
            raise mglyph_errors.BadRequestError("Challenge has no evaluation rounds")#, mglyph_errors.ErrorCode.BAD_REQUEST_INVALID_REFERENCE)
        
        if await self.malleable_glyph_repository.does_user_have_mglyph_in_challenge(current_user_id, challenge_id):
            raise mglyph_errors.BadRequestError("User has already submitted a malleable glyph for this challenge")# TODO: , mglyph_errors.ErrorCode.BAD_REQUEST_INVALID_REFERENCE)
        
        self.db_session.add(db_mglyph)
        await self.db_session.flush()  # Flush to get the ID of the new malleable glyph for evaluation linking

        # Add initial mglyph evaluation
        await self.mglyph_evaluation_service.create_evaluation_for_mglyph(db_mglyph.id, db_first_eval_round.id)
        db_mglyph = await self.malleable_glyph_repository.get_malleable_glyph_by_id(db_mglyph.id, load_options=MalleableGlyphRepository.LoadOptions.all_options())
        return db_mglyph
    


    

def get_malleable_glyph_service(
        db_session: SessionDep,
        malleable_glyph_repository: MalleableGlyphRepositoryDep,
        evaluation_round_repository: EvaluationRoundRepositoryDep,
        challenge_repository: ChallengeRepositoryDep,
        mglyph_evaluation_service: MGlyphEvaluationServiceDep):
    return MalleableGlyphService(
        db_session,
        malleable_glyph_repository,
        evaluation_round_repository,
        challenge_repository,
        mglyph_evaluation_service)

MalleableGlyphServiceDep = Annotated[MalleableGlyphService, Depends(get_malleable_glyph_service)]
