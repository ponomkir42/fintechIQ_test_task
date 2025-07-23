from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.core.schemas.mixins import TimeStampMixinSchema


class BlacklistCreate(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=255,
        pattern=r"^[а-яА-ЯёЁ]+$",
        json_schema_extra={"example": "Петр"},
    )
    last_name: str = Field(
        min_length=2,
        max_length=255,
        pattern=r"^[а-яА-ЯёЁ]+$",
        json_schema_extra={"example": "Иванов"},
    )
    middle_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        pattern=r"^[а-яА-ЯёЁ]+$",
        json_schema_extra={"example": "Сергеевич"},
    )
    birth_date: date = Field(
        gt=date(1900, 1, 1),
        json_schema_extra={"example": "1985-12-31"}
    )
    reason_id: int = Field(gt=0)

    @field_validator("middle_name", mode="after")
    def normalize_middle_name(cls, middle_name: Optional[str]) -> str:
        return middle_name or ""


class BlacklistUpdate(BaseModel):
    first_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        pattern=r"^[а-яА-ЯёЁ]+$",
        json_schema_extra={"example": "Петр"},
    )
    last_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        pattern=r"^[а-яА-ЯёЁ]+$",
        json_schema_extra={"example": "Иванов"},
    )
    middle_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        pattern=r"^[а-яА-ЯёЁ]+$",
        json_schema_extra={"example": "Сергеевич"},
    )
    birth_date: Optional[date] = Field(
        None,
        gt=date(1900, 1, 1),
        json_schema_extra={"example": "1985-12-31"}
    )
    reason_id: Optional[int] = None

    @field_validator("middle_name", mode="after")
    def normalize_middle_name(cls, middle_name: Optional[str]) -> str:
        return middle_name or ""


class BlacklistRead(TimeStampMixinSchema):
    id: UUID
    first_name: str
    last_name: str
    middle_name: Optional[str]
    reason_id: int
