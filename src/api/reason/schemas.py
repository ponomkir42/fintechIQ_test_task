from typing import Optional

from pydantic import BaseModel, Field

from src.core.schemas.mixins import TimeStampMixinSchema


class ReasonCreate(BaseModel):
    name: str = Field(max_length=255)
    slug: str = Field(max_length=50)
    description: str = Field(max_length=1000)


class ReasonUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)


class ReasonRead(TimeStampMixinSchema, ReasonCreate):
    id: int
