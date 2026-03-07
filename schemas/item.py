from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Payload for creating a new item."""
    pass


class ItemUpdate(BaseModel):
    """Partial update payload – all fields optional."""

    title: str | None = None
    description: str | None = None


class ItemResponse(ItemBase):
    """Response schema returned by all item endpoints."""

    id: int
    owner_id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
