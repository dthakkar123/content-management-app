"""
Pydantic schemas for Theme API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ThemeBase(BaseModel):
    """Base theme schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class ThemeCreate(ThemeBase):
    """Schema for creating a theme"""
    pass


class ThemeUpdate(BaseModel):
    """Schema for updating a theme"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class ThemeResponse(ThemeBase):
    """Theme response schema"""
    id: int
    content_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
