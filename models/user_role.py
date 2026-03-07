from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel

if TYPE_CHECKING:
    from models.user import User


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    # One role can belong to many users
    users: Mapped[list["User"]] = relationship("User", back_populates="role")
