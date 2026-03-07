# File: related.py
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    users = relationship("User", back_populates="role")
