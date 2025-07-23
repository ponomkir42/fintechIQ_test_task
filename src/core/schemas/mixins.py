from datetime import datetime

from pydantic import BaseModel


class TimeStampMixinSchema(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
