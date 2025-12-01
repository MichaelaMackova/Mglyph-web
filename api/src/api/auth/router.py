from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlmodel import select

from api.auth.schemas import CredentialDTO, LoggedInUserDTO, UserPublicDTO
from api.auth.utils import create_access_token, create_refresh_token
from api.auth.dependencies import validate_refresh_token
from db.models.userModel import UserModel
from db.database import SessionDep
from settings import GOOGLE_CLIENT_ID

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # responses={404: {"description": "Not found"}},
)

@router.post("/google/")
def google_auth(credential: CredentialDTO, db: SessionDep) -> LoggedInUserDTO:
    try:
        # Exchange the authorization code for an ID token
        token_request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credential.credential, token_request, GOOGLE_CLIENT_ID
        )
        # Check if the token is valid and the user is authenticated
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        # Here you can store the user information or generate a custom token
        # create user if not exists
        db_user = db.exec(
            select(UserModel)
                .where(UserModel.google_sub == id_info['sub'])
        ).first()
        if not db_user:
            # create new user
            db_user = UserModel(
                email=id_info['email'],
                google_sub=id_info['sub'],
                count=0
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        user_info = UserPublicDTO.from_model(db_user)
        return LoggedInUserDTO(
            access_token=create_access_token(user_id=str(user_info.id)),
            refresh_token=create_refresh_token(user_id=str(user_info.id)),
            user_info=user_info
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/refresh/")
def refresh_token(user_id: Annotated[str, Depends(validate_refresh_token)], db: SessionDep) -> LoggedInUserDTO:
    db_user = db.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_info = UserPublicDTO.from_model(db_user)
    return LoggedInUserDTO(
        access_token=create_access_token(user_id=str(user_info.id)),
        refresh_token=create_refresh_token(user_id=str(user_info.id)),
        user_info=user_info
    )
