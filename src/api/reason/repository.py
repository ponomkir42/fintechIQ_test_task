from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.api.reason.schemas import ReasonCreate, ReasonUpdate
from src.core.repository.base import BaseRepository
from src.models import Blacklist, Reason


class ReasonRepository(BaseRepository[Reason]):
    def __init__(self, session):
        super().__init__(session, Reason)

    async def create(self, reason: ReasonCreate) -> Reason:
        try:
            return await super().create(reason.model_dump())
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Reason with this slug already exists")

    async def update(self, reason_id: int, data: ReasonUpdate) -> Reason:
        try:
            updated = await super().update(reason_id, data.model_dump(exclude_none=True))
            if not updated:
                raise HTTPException(status_code=404, detail="Reason not found")
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Reason with this slug already exists")

    async def delete(self, reason_id: int) -> None:
        exists = await self.session.execute(
            select(Blacklist).where(Blacklist.reason_id == reason_id).limit(1)
        )
        if exists.scalar():
            raise HTTPException(status_code=400, detail="Reason is used and cannot be deleted")
        deleted = await super().delete(reason_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Reason not found")
