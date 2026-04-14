from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    team_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True
