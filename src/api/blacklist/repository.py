from typing import Any, Dict, Optional
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError
from fastapi import HTTPException
from sqlalchemy import func, select, tuple_
from sqlalchemy.exc import IntegrityError

from src.api.blacklist.schemas import BlacklistCreate, BlacklistUpdate
from src.core.repository.base import BaseRepository
from src.models import Blacklist


class BlacklistRepository(BaseRepository[Blacklist]):
    def __init__(self, session):
        super().__init__(session, Blacklist)

    async def create(self, data: BlacklistCreate) -> Blacklist:
        try:
            return await super().create(data.model_dump())
        except IntegrityError as e:
            await self.session.rollback()
            if isinstance(e.__cause__.__cause__, ForeignKeyViolationError):
                raise HTTPException(status_code=400, detail="Invalid reason reference")
            raise HTTPException(status_code=409, detail="Duplicate blacklist entry")

    async def update(self, obj_id: UUID, data: BlacklistUpdate) -> Blacklist:
        try:
            updated = await super().update(obj_id, data.model_dump(exclude_none=True))
            if not updated:
                raise HTTPException(status_code=404, detail="Blacklist entry not found")
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Duplicate blacklist entry")

    async def search(
        self,
        first_name: str,
        last_name: str,
        middle_name: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Dict[str, Any]:
        stmt = select(self.model)
        if last_name:
            stmt = stmt.where(self.model.last_name == last_name)
        if first_name:
            stmt = stmt.where(self.model.first_name == first_name)
        if middle_name:
            stmt = stmt.where(self.model.middle_name == middle_name)

        total_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total_res = await self.session.execute(total_stmt)
        total = total_res.scalar_one()

        if hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            stmt = stmt.order_by(col.desc() if order_desc else col)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return {"total": total, "items": items}

    async def get_existing_by_keys(self, keys: list) -> list[Blacklist]:
        stmt = select(self.model).where(
            tuple_(
                self.model.first_name,
                self.model.last_name,
                self.model.middle_name,
                self.model.birth_date,
            ).in_(keys)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
