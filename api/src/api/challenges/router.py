from typing import Annotated
from pydantic import ValidationError
from fastapi import APIRouter, Query, HTTPException, status
from sqlmodel import select
from db.database import SessionDep

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep
from uuid import UUID

from db.models.challengeModel import ChallengeModel
from api.challenges.schemas import ChallengePublicDTO, ChallengeCreateDTO
from db.models.userModel import UserModel
from db.models.evaluationRoundModel import EvaluationRoundModel

router = APIRouter(
    prefix="/challenges",
    tags=["challenges"],
    # responses={404: {"description": "Not found"}},
)



@router.post("")
def create_challenge(challenge: ChallengeCreateDTO, current_user_id: CurrentAdminUserIdDep, session: SessionDep) -> ChallengePublicDTO:
    # TODO: ověřit, že je aktivní uživatel admin
    try:
        db_challenge = ChallengeModel.model_validate(challenge)
        db_challenge.id = None  # Ensure ID is None for new records
        db_challenge.creator_id = current_user_id
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    session.add(db_challenge)
    session.commit()
    session.refresh(db_challenge)
    new_challenge = ChallengePublicDTO.from_model(db_challenge)
    return new_challenge
    


@router.get("")
def read_challenges():
    pass


@router.get("/{challenge_id}")
def read_challenge(challenge_id: UUID):
    pass


@router.patch("/{challenge_id}")
def update_challenge(challenge_id: UUID):
    pass


@router.post("/{challenge_id}/add-solver")
def add_self_as_solver(challenge_id: UUID, user_id: CurrentUserIdDep, session: SessionDep):
    challenge_db = session.get(ChallengeModel, challenge_id)
    if not challenge_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    current_user_db = session.get(UserModel, UUID(user_id))
    if not current_user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user_db in challenge_db.solvers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a solver of this challenge")
    challenge_db.solvers.append(current_user_db)
    session.add(challenge_db)
    session.commit()
    session.refresh(challenge_db)
    return ChallengePublicDTO.from_model(challenge_db)


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