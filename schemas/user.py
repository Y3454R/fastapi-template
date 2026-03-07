from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    role_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None
    is_active: bool | None = None
    role_id: int | None = None


class UserResponse(UserBase):
    id: int
    role_id: int | None

    model_config = ConfigDict(from_attributes=True)
