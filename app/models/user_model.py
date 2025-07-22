from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.models.base import Base, IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str | None] = mapped_column(String, nullable=True)

    auth_provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="local"
    )
    oauth_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
