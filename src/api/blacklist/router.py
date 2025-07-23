from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.blacklist.repository import BlacklistRepository
from src.api.blacklist.schemas import BlacklistCreate, BlacklistRead, BlacklistUpdate
from src.core.config import config
from src.core.database.connector import get_db_session
from src.core.schemas.response_schemas import PaginatedResponse, QueryParams

router = APIRouter()


@router.get("")
async def list_blacklist(
    params: QueryParams = Depends(QueryParams),
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse[BlacklistRead]:
    repo = BlacklistRepository(session)
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


@router.get("/search/", response_model=PaginatedResponse[BlacklistRead])
async def search_blacklist(
    first_name: str,
    last_name: str,
    middle_name: str | None = None,
    params: QueryParams = Depends(QueryParams),
    session: AsyncSession = Depends(get_db_session),
):
    repo = BlacklistRepository(session)
    data = await repo.search(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
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


@router.post("/queue/")
async def queue_blacklist(
    payload: List[BlacklistCreate],
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    repo = BlacklistRepository(session)
    producer = request.app.state.rabbit_producer

    keys = [(p.first_name, p.last_name, p.middle_name, p.birth_date) for p in payload]

    existing_keys = {
        (e.first_name, e.last_name, e.middle_name, e.birth_date)
        for e in await repo.get_existing_by_keys(keys)
    }

    successes = []
    errors = []

    for person in payload:
        key = (person.first_name, person.last_name, person.middle_name, person.birth_date)
        if key in existing_keys:
            errors.append({"item": person.model_dump(mode="json"), "error": "Duplicate"})
        else:
            await producer.send_message(config.RABBIT_QUEUE, person.model_dump(mode="json"))
            successes.append(person.model_dump(mode="json"))

    if errors:
        return JSONResponse(
            status_code=status.HTTP_207_MULTI_STATUS,
            content={"sent": successes, "errors": errors},
        )

    return {"sent": successes}


@router.get("/{entry_id}/")
async def get_blacklist_entry(
    entry_id: UUID, session: AsyncSession = Depends(get_db_session)
) -> BlacklistRead:
    repo = BlacklistRepository(session)
    entry = await repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Blacklist entry not found")
    return entry


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_blacklist_entries(
    payload: List[BlacklistCreate], session: AsyncSession = Depends(get_db_session)
) -> list[BlacklistRead]:
    repo = BlacklistRepository(session)
    created = []
    errors = []
    for item in payload:
        try:
            entry = await repo.create(item)
            created.append(entry)
        except HTTPException as e:
            errors.append({"item": item.model_dump(mode="json"), "error": e.detail})
    if errors:
        return JSONResponse(
            content={
                "created": [entry.model_dump(mode="json") for entry in created],
                "errors": errors,
            },
            status_code=status.HTTP_207_MULTI_STATUS,
        )
    return created


@router.patch("/{entry_id}/")
async def update_blacklist_entry(
    entry_id: UUID, payload: BlacklistUpdate, session: AsyncSession = Depends(get_db_session)
) -> BlacklistRead:
    repo = BlacklistRepository(session)
    return await repo.update(entry_id, payload)


@router.delete("/{entry_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blacklist_entry(entry_id: UUID, session: AsyncSession = Depends(get_db_session)):
    repo = BlacklistRepository(session)
    success = await repo.delete(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blacklist entry not found")
