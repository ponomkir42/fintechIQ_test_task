from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.mixins import TimestampMixin
from src.models.base import Base


class Reason(Base, TimestampMixin):
    __tablename__ = "reasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
