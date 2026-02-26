from typing import Annotated
from fastapi import APIRouter, Query, HTTPException, status, responses
from uuid import UUID
from db.database import SessionDep
from pydantic import ValidationError
from errors import NotFoundError, BadRequestError

from api.auth.dependencies import CurrentAdminUserIdDep, CurrentUserIdDep
from api.users.services import UserServiceDep

from api.users.schemas import UserPublicSimpleDTO, UserPublicDTO



router = APIRouter(
    prefix="/users",
    tags=["users"],
)



@router.get("")
async def read_users(
    user_service: UserServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
) -> list[UserPublicSimpleDTO]:
    users = await user_service.get_paginated_users(offset=offset, limit=limit)
    return [UserPublicSimpleDTO.from_model(user) for user in users]


@router.get("/{user_id}",
            responses={
                NotFoundError.http_code: NotFoundError.response_dict()
             })
async def read_user_by_id(
    user_id: UUID,
    user_service: UserServiceDep
) -> UserPublicDTO:
    try:
        user = await user_service.get_user_by_id(user_id)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    return UserPublicDTO.from_model(user)


@router.patch("/{user_id}/give-admin-role/",
              responses={
                NotFoundError.http_code: NotFoundError.response_dict(),
                BadRequestError.http_code: BadRequestError.response_dict()
             })
async def give_admin_role(
    user_id: UUID,
    user_service: UserServiceDep,
    current_user_id: CurrentAdminUserIdDep
) -> UserPublicSimpleDTO:
    try:
        user = await user_service.give_admin_role(user_id)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)
    return UserPublicSimpleDTO.from_model(user)


@router.patch("/{user_id}/revoke-admin-role/",
              responses={
                NotFoundError.http_code: NotFoundError.response_dict(),
                BadRequestError.http_code: BadRequestError.response_dict()
             })
async def revoke_admin_role(
    user_id: UUID,
    user_service: UserServiceDep,
    current_user_id: CurrentAdminUserIdDep
) -> UserPublicSimpleDTO:
    try:
        user = await user_service.revoke_admin_role(user_id)
    except NotFoundError as e:
        raise NotFoundError.HTTPException(e)
    except BadRequestError as e:
        raise BadRequestError.HTTPException(e)
    return UserPublicSimpleDTO.from_model(user)