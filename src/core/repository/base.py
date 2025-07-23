from typing import Any, Dict, Generic, Optional, Type, TypeVar

from sqlalchemy import delete, func, insert, select
from sqlalchemy import update as sa_update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_all(self, limit: int, offset: int, order_by: str, order_desc: bool) -> dict:
        stmt = select(self.model)
        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            stmt = stmt.order_by(col.desc() if order_desc else col)
        total = await self.session.execute(select(func.count()).select_from(self.model))
        result = await self.session.execute(stmt.limit(limit).offset(offset))
        return {"total": total.scalar_one(), "items": result.scalars().all()}

    async def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        return await self.session.get(self.model, obj_id)

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        stmt = insert(self.model).values(**obj_in).returning(self.model)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update(self, obj_id: int, obj_in: Dict[str, Any]) -> ModelType:
        stmt = (
            sa_update(self.model)
            .where(self.model.id == obj_id)
            .values(**obj_in)
            .returning(self.model)
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
        except NoResultFound:
            raise
        updated = result.scalar_one_or_none()
        if not updated:
            return None
        return updated

    async def delete(self, obj_id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
