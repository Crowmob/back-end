from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Boolean, LargeBinary

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
    identities = relationship("Identities", back_populates="user", uselist=True)


class Identities(IDMixin, Base):
    __tablename__ = "identities"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    user = relationship("User", back_populates="identities")
