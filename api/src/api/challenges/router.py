from typing import Annotated
from fastapi import APIRouter, Query, HTTPException, status, responses
from uuid import UUID

from sqlmodel import select
from db.database import SessionDep
from pydantic import ValidationError
from errors import NotFoundError, BadRequestError

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep
from api.challenges.services import ChallengeServiceDep, EvaluationRoundServiceDep


from db.models.challengeModel import ChallengeModel
from api.challenges.schemas import ChallengePublicDTO, ChallengePublicSimpleDTO, ChallengeCreateDTO
from db.models.userModel import UserModel
from db.models.evaluationRoundModel import EvaluationRoundModel

router = APIRouter(
    prefix="/challenges",
    tags=["challenges"],
)



@router.post("", 
             status_code=status.HTTP_201_CREATED, 
             response_description="Challenge Created Successfully")
async def create_challenge(challenge: ChallengeCreateDTO, current_user_id: CurrentAdminUserIdDep, challenge_service: ChallengeServiceDep) -> ChallengePublicDTO:
    try:
        new_challenge = await challenge_service.create_challenge(challenge, UUID(current_user_id))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ChallengePublicDTO.from_model(new_challenge)
    


@router.get("")
async def read_challenges(
    challenge_service: ChallengeServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
) -> list[ChallengePublicSimpleDTO]:
    challenges = await challenge_service.get_paginated_challenges(offset=offset, limit=limit)
    return [ChallengePublicSimpleDTO.from_model(challenge) for challenge in challenges]



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


#TODO: odstranit
@router.get("/{challenge_id}/test-rounds")
def get_test_rounds(challenge_id: UUID, session: SessionDep):
    challenge_db = session.get(ChallengeModel, challenge_id)
    if not challenge_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    print("Challenge rounds:", challenge_db.evaluation_rounds)

    round_one = EvaluationRoundModel(sequence_number=1, estimated_end_time="2027-12-31T23:59:59", challenge_id=challenge_id)
    session.add(round_one)
    session.commit()
    session.refresh(round_one)

    print("Challenge rounds after adding round one:", challenge_db.evaluation_rounds)
    print("Round one - next round:", round_one.next_round)
    print("Round one - previous round:", round_one.previous_round)


    round_two = EvaluationRoundModel(sequence_number=2, estimated_end_time="2028-12-31T23:59:59", challenge_id=challenge_id)
    session.add(round_two)
    round_one.next_round = round_two
    session.add(round_one)
    session.commit()
    session.refresh(round_one)
    session.refresh(round_two)

    print("Challenge rounds after adding round two:", challenge_db.evaluation_rounds)
    print("Round one - next round:", round_one.next_round)
    print("Round one - previous round:", round_one.previous_round)
    print("Round two - next round:", round_two.next_round)
    print("Round two - previous round:", round_two.previous_round)

    # delete rounds
    session.delete(round_one)
    session.delete(round_two)
    session.commit()


    return challenge_db.evaluation_rounds