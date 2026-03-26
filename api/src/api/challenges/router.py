from typing import Annotated, Optional
from fastapi import APIRouter, Query, HTTPException, status, responses
from uuid import UUID

from errors import NotFoundError, BadRequestError, ErrorCode

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep, CurrentUserIdOrNoneDep
from api.challenges.services import ChallengeServiceDep, ChallengeEvaluatorServiceDep


from api.challenges.schemas import ChallengeFilterParamsAsQuery, ChallengePublicDTO, ChallengePublicMiniDetailDTO, ChallengePublicSimpleDTO, ChallengeCreateDTO, ChallengeUserRelationshipDTO, ChallengeState
from api.mglyph.schemas import MGlyphEvaluationPublicDTO
from db.models.challengeEvaluatorModel import ChallengeEvaluatorState
from db.pagination import PagedResponse

router = APIRouter(
    prefix="/challenges",
    tags=["challenges"],
)



@router.post("", 
             description="[Admin required] Create a new challenge",
             status_code=status.HTTP_201_CREATED, 
             response_description="Challenge Created Successfully")
async def create_challenge(challenge: ChallengeCreateDTO, current_user_id: CurrentAdminUserIdDep, challenge_service: ChallengeServiceDep) -> ChallengePublicDTO:
    try:
        new_challenge = await challenge_service.create_challenge(challenge, UUID(current_user_id))
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)
    return ChallengePublicDTO.from_model(new_challenge)
    


@router.get("", description="[Optional login - added user relation info] Get a list of challenges with optional filtering and pagination",)
async def read_challenges(
    current_user_id: CurrentUserIdOrNoneDep,
    challenge_service: ChallengeServiceDep,
    filter_params: ChallengeFilterParamsAsQuery,
    glyph_count: Annotated[int, Query(le=5, ge=0, description="Include first glyph_count best ranked glyphs of the challenge in the response. Max value is 5. If not specified, no glyphs will be included.")] = 0,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20
) -> PagedResponse[ChallengePublicMiniDetailDTO]:
    #TODO: získat glyfy i z jiných kol než jen z aktuálního?
    challenges_with_glyphs_and_user_relationship = await challenge_service.get_paginated_challenges_with_glyphs_and_user_relationship(filters=filter_params, current_user_id=UUID(current_user_id) if current_user_id else None, glyph_count=glyph_count, page=page, size=size)
    challenges_with_glyphs_and_user_relationship.items = [
        ChallengePublicMiniDetailDTO(
            id=item["challenge"].id,
            name=item["challenge"].name,
            glyph_submit_deadline=item["challenge"].glyph_submit_deadline,
            state=ChallengeState.from_model_params(item["challenge"].challenge_finished, item["challenge"].submissions_ended),
            mglyph_evaluations=[MGlyphEvaluationPublicDTO.from_model(mglyph_evaluation) for mglyph_evaluation in item["glyphs"]],
            user_relationship=ChallengeUserRelationshipDTO.from_relationship_flags(
                is_solver=item["user_relationship"]["is_solver"],
                has_submitted_mglyph=item["user_relationship"]["has_submitted_mglyph"],
                is_evaluator=item["user_relationship"]["is_evaluator"],
                waiting_for_evaluation=item["user_relationship"]["waiting_for_evaluation"]
            ) if item["user_relationship"] else None
        )
        for item in challenges_with_glyphs_and_user_relationship.items
    ]
    return challenges_with_glyphs_and_user_relationship

@router.get("/user-is-participant", description="[Login required] Get a list of challenges where the logged in user is a participant (solver or evaluator) with optional filtering and pagination")
async def read_challenges_where_user_is_participant(
    challenge_service: ChallengeServiceDep,
    user_id: CurrentUserIdDep,
    filter_params: ChallengeFilterParamsAsQuery,
    as_solver: Optional[bool] = Query(default=None, description="If true, only return challenges where the user is a solver. If false, only return challenges where the user is evaluator. If null, return all challenges where the user is either a solver or evaluator."),
    glyph_count: Annotated[int, Query(le=5, ge=0, description="Include first glyph_count best ranked glyphs of the challenge in the response. Max value is 5. If not specified, no glyphs will be included.")] = 0,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20
) -> PagedResponse[ChallengePublicMiniDetailDTO]:
    challenges_with_glyphs_and_user_relationship = await challenge_service.get_challenges_where_user_is_participant_with_glyphs_and_user_relationship(user_id=UUID(user_id), filters=filter_params, as_solver=as_solver, glyph_count=glyph_count, page=page, size=size)
    challenges_with_glyphs_and_user_relationship.items = [
        ChallengePublicMiniDetailDTO(
            id=item["challenge"].id,
            name=item["challenge"].name,
            glyph_submit_deadline=item["challenge"].glyph_submit_deadline,
            state=ChallengeState.from_model_params(item["challenge"].challenge_finished, item["challenge"].submissions_ended),
            mglyph_evaluations=[MGlyphEvaluationPublicDTO.from_model(mglyph_evaluation) for mglyph_evaluation in item["glyphs"]],
            user_relationship=ChallengeUserRelationshipDTO.from_relationship_flags(
                is_solver=item["user_relationship"]["is_solver"],
                has_submitted_mglyph=item["user_relationship"]["has_submitted_mglyph"],
                is_evaluator=item["user_relationship"]["is_evaluator"],
                waiting_for_evaluation=item["user_relationship"]["waiting_for_evaluation"]
            ) if item["user_relationship"] else None
        )
        for item in challenges_with_glyphs_and_user_relationship.items
    ]
    return challenges_with_glyphs_and_user_relationship


@router.get("/{challenge_id}",
            responses={
                NotFoundError.http_code: NotFoundError.response_dict()
             })
async def read_challenge(challenge_id: UUID, challenge_service: ChallengeServiceDep) -> ChallengePublicDTO:
    try:
        challenge = await challenge_service.get_challenge_by_id(challenge_id)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    
    return ChallengePublicDTO.from_model(challenge)


@router.patch("/{challenge_id}")
def update_challenge(challenge_id: UUID):
    pass


@router.post("/{challenge_id}/add-solver",
                responses={
                    NotFoundError.http_code: NotFoundError.response_dict(),
                    BadRequestError.http_code: BadRequestError.response_dict()
                }
             )
async def add_self_as_solver(challenge_id: UUID, user_id: CurrentUserIdDep, challenge_service: ChallengeServiceDep) -> ChallengePublicDTO:
    try:
        challenge_db = await challenge_service.add_solver_to_challenge(challenge_id, UUID(user_id))
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)
    return ChallengePublicDTO.from_model(challenge_db)



@router.post("/{challenge_id}/volunteer-evaluator")
async def volunteer_self_as_evaluator(challenge_id: UUID, user_id: CurrentUserIdDep, challenge_service: ChallengeServiceDep) -> ChallengePublicDTO:
    try:
        challenge_db = await challenge_service.add_evaluator_to_challenge(challenge_id, UUID(user_id), is_volunteer=True)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)
    return ChallengePublicDTO.from_model(challenge_db)


@router.post("/{challenge_id}/invite-evaluator")
async def invite_evaluator(challenge_id: UUID, evaluator_user_id: UUID, current_user_id: CurrentAdminUserIdDep, challenge_service: ChallengeServiceDep) -> ChallengePublicDTO:
    try:
        challenge_db = await challenge_service.add_evaluator_to_challenge(challenge_id, evaluator_user_id, is_volunteer=False)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)
    return ChallengePublicDTO.from_model(challenge_db)



@router.post("/{challenge_id}/confirm-volunteer-evaluator/{evaluator_user_id}")
async def confirm_volunteer_evaluator(challenge_id: UUID, evaluator_user_id: UUID, current_user_id: CurrentAdminUserIdDep, challenge_evaluator_service: ChallengeEvaluatorServiceDep) -> None:
    try:
        await challenge_evaluator_service.change_state_of_challenge_evaluator(challenge_id, evaluator_user_id, ChallengeEvaluatorState.confirmed, confirm_old_state=ChallengeEvaluatorState.volunteer_pending)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        # TODO: zkontrolovat error code a vrátit lepší odpověď (popřípadě nový error code) - if "state does not match" -> not a volunteer_pending -> jiný err code?
        if e.err_code == ErrorCode.BAD_REQUEST_WRONG_STATE:
            raise BadRequestError.HTTPException(BadRequestError("Challenge Evaluator is not in volunteer_pending state", ErrorCode.BAD_REQUEST_WRONG_STATE))
        raise BadRequestError.HTTPException(e)


@router.post("/{challenge_id}/reject-volunteer-evaluator/{evaluator_user_id}")
async def reject_volunteer_evaluator(challenge_id: UUID, evaluator_user_id: UUID, current_user_id: CurrentAdminUserIdDep, challenge_evaluator_service: ChallengeEvaluatorServiceDep) -> None:
    try:
        await challenge_evaluator_service.change_state_of_challenge_evaluator(challenge_id, evaluator_user_id, ChallengeEvaluatorState.volunteer_rejected, confirm_old_state=ChallengeEvaluatorState.volunteer_pending)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        # TODO: zkontrolovat error code a vrátit lepší odpověď (popřípadě nový error code) - if "state does not match" -> not a volunteer_pending -> jiný err code?
        if e.err_code == ErrorCode.BAD_REQUEST_WRONG_STATE:
            raise BadRequestError.HTTPException(BadRequestError("Challenge Evaluator is not in volunteer_pending state", ErrorCode.BAD_REQUEST_WRONG_STATE))
        raise BadRequestError.HTTPException(e)


@router.post("/{challenge_id}/confirm-evaluator-invite")
async def confirm_evaluator_invite(challenge_id: UUID, current_user_id: CurrentUserIdDep, challenge_evaluator_service: ChallengeEvaluatorServiceDep) -> None:
    try:
        await challenge_evaluator_service.change_state_of_challenge_evaluator(challenge_id, UUID(current_user_id), ChallengeEvaluatorState.confirmed, confirm_old_state=ChallengeEvaluatorState.invited_pending)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        # TODO: zkontrolovat error code a vrátit lepší odpověď (popřípadě nový error code) - if "state does not match" -> not a volunteer_pending -> jiný err code?
        if e.err_code == ErrorCode.BAD_REQUEST_WRONG_STATE:
            raise BadRequestError.HTTPException(BadRequestError("Challenge Evaluator is not in invited_pending state", ErrorCode.BAD_REQUEST_WRONG_STATE))
        raise BadRequestError.HTTPException(e)


@router.post("/{challenge_id}/reject-evaluator-invite")
async def reject_evaluator_invite(challenge_id: UUID, current_user_id: CurrentUserIdDep, challenge_evaluator_service: ChallengeEvaluatorServiceDep) -> None:
    try:
        await challenge_evaluator_service.change_state_of_challenge_evaluator(challenge_id, UUID(current_user_id), ChallengeEvaluatorState.invited_rejected, confirm_old_state=ChallengeEvaluatorState.invited_pending)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        # TODO: zkontrolovat error code a vrátit lepší odpověď (popřípadě nový error code) - if "state does not match" -> not a volunteer_pending -> jiný err code?
        if e.err_code == ErrorCode.BAD_REQUEST_WRONG_STATE:
            raise BadRequestError.HTTPException(BadRequestError("Challenge Evaluator is not in invited_pending state", ErrorCode.BAD_REQUEST_WRONG_STATE))
        raise BadRequestError.HTTPException(e)
    


@router.delete("/{challenge_id}", 
                status_code=status.HTTP_204_NO_CONTENT,
                responses={
                    status.HTTP_204_NO_CONTENT: {"description": "Challenge Deleted Successfully"},
                    NotFoundError.http_code: NotFoundError.response_dict()
                    }
            )
async def delete_challenge(challenge_id: UUID, current_user_id: CurrentAdminUserIdDep, challenge_service: ChallengeServiceDep):
    try:
        await challenge_service.delete_challenge(challenge_id)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)

