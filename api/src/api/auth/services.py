from typing import Annotated
from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import SessionDep
from uuid import UUID
import errors as mglyph_errors
from google.oauth2 import id_token
from google.auth.transport import requests
from settings import GOOGLE_CLIENT_ID


from db.repos.userRepository import UserRepository, UserRepositoryDep

from api.users.schemas import UserPublicDTO, UserCreateDTO, UserUpdateDTO
from api.auth.schemas import CredentialDTO, LoggedInUserDTO, GoogleUserCreateDTO



class AuthService:
    def __init__(
            self, 
            db_session: AsyncSession, 
            user_repository: UserRepository
            ):
        self.db_session = db_session
        self.user_repository = user_repository


    def get_google_user_info(self, credential: CredentialDTO) -> dict:
        # Exchange the authorization code for an ID token
        token_request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credential.credential, token_request, GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
        )
        # Check if the token is valid and the user is authenticated
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise mglyph_errors.UnauthorizedError("Invalid token issuer", mglyph_errors.ErrorCode.UNAUTHORIZED_INVALID_TOKEN)
        return id_info



def get_auth_service(
    db_session: SessionDep,
    user_repository: UserRepositoryDep
) -> AuthService:
    return AuthService(db_session, user_repository)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]