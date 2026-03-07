from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from models.base import BaseModel

if TYPE_CHECKING:
    from models.user import User


class Item(BaseModel):
    """
    Example CRUD resource. Replace this with your own domain model.

    Demonstrates the standard pattern:
    - Auto-incremented ``id``, ``created_at``, ``updated_at`` from BaseModel
    - Soft-delete via ``is_deleted`` flag
    - Foreign-key ownership linked to a User
    """

    __tablename__ = "items"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Ownership – every item belongs to the user who created it
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="items")
