from typing import Annotated
from pydantic import ValidationError
from fastapi import APIRouter, Query, HTTPException, status
from sqlmodel import select
from db.database import SessionDep

from api.auth.dependencies import CurrentUserIdDep
from uuid import UUID

from db.models.challengeModel import ChallengeModel
from api.challenges.schemas import ChallengePublicDTO, ChallengeCreateDTO
from db.models.userModel import UserModel

router = APIRouter(
    prefix="/challenges",
    tags=["challenges"],
    # responses={404: {"description": "Not found"}},
)



@router.post("")
def create_challenge(challenge: ChallengeCreateDTO, session: SessionDep) -> ChallengePublicDTO:
    # TODO: ověřit, že je aktivní uživatel admin
    try:
        db_challenge = ChallengeModel.model_validate(challenge)
        db_challenge.id = None  # Ensure ID is None for new records
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


@router.post("/{challenge_id}/add-self-as-solver")
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
    