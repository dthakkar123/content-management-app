"""
Pydantic schemas for Search API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.content import ContentResponse


class SearchRequest(BaseModel):
    """Search request parameters"""
    q: Optional[str] = Field(None, description="Search query")
    theme_ids: Optional[List[int]] = Field(None, description="Filter by theme IDs")
    source_types: Optional[List[str]] = Field(None, description="Filter by source types (twitter, pdf, arxiv, acm, web)")
    date_from: Optional[datetime] = Field(None, description="Filter by date from")
    date_to: Optional[datetime] = Field(None, description="Filter by date to")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "q": "machine learning",
                "theme_ids": [1, 2],
                "source_types": ["arxiv", "web"],
                "page": 1,
                "page_size": 10
            }
        }


class SearchResponse(BaseModel):
    """Search response with results"""
    query: Optional[str]
    items: List[ContentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
