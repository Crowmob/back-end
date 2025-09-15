from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Boolean

from app.models.base import Base, IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    about: Mapped[str] = mapped_column(String(512), nullable=True)
    avatar_ext: Mapped[str | None] = mapped_column(String(32), nullable=True)
    has_profile: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
