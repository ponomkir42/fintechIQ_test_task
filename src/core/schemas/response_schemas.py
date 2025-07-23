from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field, computed_field


PydanticModel = TypeVar("PydanticModel")


class MetaData(BaseModel):
    found: int
    limit: int
    page: int


class PaginatedResponse(BaseModel, Generic[PydanticModel]):
    meta: MetaData
    items: List[PydanticModel]


class QueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    order_by: str = "created_at"
    order_desc: bool = False

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
