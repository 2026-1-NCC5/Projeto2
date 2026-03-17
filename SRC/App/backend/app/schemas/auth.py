from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole