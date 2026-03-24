from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    team_id: Optional[int] = None
    active: bool = True


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    team_id: Optional[int] = None
    active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    team_id: Optional[int] = None
    active: bool

    class Config:
        from_attributes = True