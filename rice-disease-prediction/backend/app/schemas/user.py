"""
Pydantic schemas for User endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str = Field(..., min_length=5, max_length=255, examples=["farmer@example.com"])
    password: str = Field(..., min_length=6, max_length=128)
    name: str = Field(..., min_length=1, max_length=255, examples=["John Doe"])


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str = Field(..., examples=["farmer@example.com"])
    password: str = Field(...)


class UserResponse(BaseModel):
    """Schema for user profile response."""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token payload."""
    user_id: Optional[str] = None
