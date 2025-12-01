from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from api.count.schemas import CountDTO
from api.auth.dependencies import CurrentUserIdDep
from db.database import SessionDep
from db.models.userModel import UserModel

router = APIRouter(
    prefix="/count",
    tags=["count"],
    # responses={404: {"description": "Not found"}},
)

@router.get("/add-one/")
def add_count(user_id: CurrentUserIdDep, db: SessionDep) -> CountDTO:
    db_user = db.get(UserModel, UUID(user_id))
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user.count += 1
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return CountDTO(count=db_user.count)

@router.get("/")
def get_count(user_id: CurrentUserIdDep, db: SessionDep) -> CountDTO:
    db_user = db.get(UserModel, UUID(user_id))
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return CountDTO(count=db_user.count)
