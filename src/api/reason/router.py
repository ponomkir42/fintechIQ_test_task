from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.reason.repository import ReasonRepository
from src.api.reason.schemas import ReasonCreate, ReasonRead, ReasonUpdate
from src.core.database.connector import get_db_session
from src.core.schemas.response_schemas import PaginatedResponse, QueryParams

router = APIRouter()


@router.get("")
async def list_reasons(
    params: QueryParams = Depends(QueryParams),
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse[ReasonRead]:
    repo = ReasonRepository(session)
    data = await repo.get_all(
        limit=params.limit,
        offset=params.offset,
        order_by=params.order_by,
        order_desc=params.order_desc,
    )
    return PaginatedResponse(
        meta={
            "found": data["total"],
            "page": params.page,
            "limit": params.limit,
        },
        items=data["items"],
    )


@router.get("/{entry_id}/")
async def get_reason(entry_id: int, session: AsyncSession = Depends(get_db_session)) -> ReasonRead:
    repo = ReasonRepository(session)
    entry = await repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Reason not found")
    return entry


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_reason(
    reason: ReasonCreate, session: AsyncSession = Depends(get_db_session)
) -> ReasonRead:
    repo = ReasonRepository(session)
    return await repo.create(reason)


@router.patch("/{reason_id}/")
async def update_reason(
    reason_id: int, reason: ReasonUpdate, session: AsyncSession = Depends(get_db_session)
) -> ReasonRead:
    repo = ReasonRepository(session)
    return await repo.update(reason_id, reason)


@router.delete("/{reason_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reason(reason_id: int, session: AsyncSession = Depends(get_db_session)):
    repo = ReasonRepository(session)
    await repo.delete(reason_id)
