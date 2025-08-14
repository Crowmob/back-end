from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey

from app.models.base import Base, IDMixin, TimestampMixin


class Memberships(Base, IDMixin, TimestampMixin):
    __tablename__ = "memberships"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")


class MembershipRequests(Base, IDMixin, TimestampMixin):
    __tablename__ = "membership_requests"

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_id: Mapped[int] = mapped_column(Integer, nullable=False)
