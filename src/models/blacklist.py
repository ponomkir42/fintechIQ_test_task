from datetime import date
from uuid import uuid4

from sqlalchemy import UUID, Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.mixins import TimestampMixin
from src.models.base import Base
from src.models.reason import Reason


class Blacklist(Base, TimestampMixin):
    __tablename__ = "blacklist_customers"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)

    reason_id: Mapped[int] = mapped_column(ForeignKey("reasons.id"), nullable=False)
    reason: Mapped["Reason"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "middle_name",
            "birth_date",
            name="unique_blacklist_per_full_name_and_birth_date",
        ),
        Index("idx_blacklist_search_full", "last_name", "first_name", "middle_name"),
    )
