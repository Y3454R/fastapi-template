from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel

if TYPE_CHECKING:
    from models.user_role import UserRole
    from models.item import Item


class User(BaseModel):
    """
    Represents a registered user account.

    Relationships:
        role: Optional :class:`~models.user_role.UserRole` assigned to the user.
        items: All :class:`~models.item.Item` records owned by this user.
               Cascade-deleted when the user is removed.
    """

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_roles.id"), nullable=True
    )
    role: Mapped["UserRole"] = relationship("UserRole", back_populates="users")

    # Cascade-delete: removing a user removes all their items
    items: Mapped[list["Item"]] = relationship(
        "Item", back_populates="owner", cascade="all, delete-orphan"
    )
