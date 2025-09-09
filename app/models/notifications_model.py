from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, Enum

from app.core.enums.enums import NotificationStatus
from app.models.base import Base, IDMixin, TimestampMixin


class Notification(IDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    status: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    message: Mapped[str] = mapped_column(
        Enum(NotificationStatus, name="role_enum"),
        nullable=False,
        default=NotificationStatus.UNREAD,
    )
