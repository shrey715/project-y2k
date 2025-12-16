from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Schema for detailed user response."""
    images_cnt: int = 0
    audios_cnt: int = 0
