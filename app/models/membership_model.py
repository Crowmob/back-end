from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

from app.models.base import Base, IDMixin, TimestampMixin
from app.core.enums.enums import RoleEnum


class Memberships(Base, IDMixin, TimestampMixin):
    __tablename__ = "memberships"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.MEMBER
    )


class MembershipRequests(Base, IDMixin, TimestampMixin):
    __tablename__ = "membership_requests"

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
