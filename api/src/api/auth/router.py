from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from uuid import UUID
import errors as mglyph_errors
from api.auth.services import AuthServiceDep
from api.users.services import UserServiceDep
from db.repos.userRepository import UserRepositoryDep
from api.auth.schemas import CredentialDTO, LoggedInUserDTO, GoogleUserCreateDTO
from api.users.schemas import UserPublicSimpleDTO, UserCreateDTO
from api.auth.dependencies import validate_refresh_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # responses={404: {"description": "Not found"}},
)

@router.post("/google/")
async def google_auth(credential: CredentialDTO, user_repo: UserRepositoryDep, auth_service: AuthServiceDep) -> LoggedInUserDTO:
    try:
        id_info = auth_service.get_google_user_info(credential)
    except mglyph_errors.UnauthorizedError as e:
        raise mglyph_errors.UnauthorizedError.HTTPException(e)
    db_user = await user_repo.get_user_by_google_sub(id_info['sub'])
    if not db_user:
        err = mglyph_errors.NotFoundError("Google user", mglyph_errors.ErrorCode.NOT_FOUND_LOGGED_IN_USER)
        raise mglyph_errors.NotFoundError.HTTPException(err)
    user_info = UserPublicSimpleDTO.from_model(db_user)
    return LoggedInUserDTO.init_with_new_tokens(user_info)
    

@router.post("/google/create-user/")
async def google_auth_create_user(google_user: GoogleUserCreateDTO, auth_service: AuthServiceDep, user_service: UserServiceDep) -> LoggedInUserDTO:
    try:
        id_info = auth_service.get_google_user_info(google_user.credential)
    except mglyph_errors.UnauthorizedError as e:
        raise mglyph_errors.UnauthorizedError.HTTPException(e)
    # Create new user
    user_create = UserCreateDTO(
        username=google_user.username,
        email=id_info['email'],
        google_sub=id_info['sub']
    )
    db_user = await user_service.create_user(user_create)
    return LoggedInUserDTO.init_with_new_tokens(UserPublicSimpleDTO.from_model(db_user))



@router.get("/refresh/")
async def refresh_token(user_id: Annotated[str, Depends(validate_refresh_token)], user_repo: UserRepositoryDep) -> LoggedInUserDTO:
    db_user = await user_repo.get_user_by_id(UUID(user_id))
    if not db_user:
        err = mglyph_errors.NotFoundError("Logged in user", mglyph_errors.ErrorCode.NOT_FOUND_LOGGED_IN_USER)
        raise mglyph_errors.NotFoundError.HTTPException(err)
    user_info = UserPublicSimpleDTO.from_model(db_user)
    return LoggedInUserDTO.init_with_new_tokens(user_info)
