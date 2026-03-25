from typing import Annotated, Generic, List, TypeVar, Callable
from pydantic import BaseModel, conint
from pydantic.generics import GenericModel
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import Select, Row
from sqlmodel import select, func, and_

class PaginationParams(BaseModel):
    """ Request query params for paginated API. """
    page: Annotated[int, conint(ge=1)] = 1
    size: Annotated[int, conint(ge=1, le=100)] = 20


T = TypeVar("T")

class PagedResponse(GenericModel, Generic[T]):
    """Response schema for any paged API."""

    items: List[T]
    total: int
    total_pages: int
    page: int
    size: int


async def paginate(db_session: AsyncSession, statement: Select, ResponseSchema: type[T], pagination_params: PaginationParams, as_scalar: bool = True, create_ResponseSchema_data: Callable[[Row], T] = None) -> PagedResponse[T]:
    """Helper function to create a paginated response."""
    stmnt_subquery = statement.subquery()
    total_result = await db_session.execute(select(func.count().label("total")).select_from(stmnt_subquery))
    total = total_result.scalar_one()
    total_pages = (total + pagination_params.size - 1) // pagination_params.size
    paged_statement = statement.offset((pagination_params.page - 1) * pagination_params.size).limit(pagination_params.size)
    result = await db_session.execute(paged_statement)
    if as_scalar:
        response_items = result.scalars().all()
    else:
        items = result.all()
        if create_ResponseSchema_data:
            response_items = [create_ResponseSchema_data(item) for item in items]
        else:
            if ResponseSchema is None:
                response_items = items
            else:
                response_items = [ResponseSchema.model_validate(item[0].model_dump()) for item in items]
    return PagedResponse[ResponseSchema](
        total=total,
        total_pages=total_pages,
        page=pagination_params.page,
        size=pagination_params.size,
        items=response_items
    )