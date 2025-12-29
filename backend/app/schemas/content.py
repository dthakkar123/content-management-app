"""
Pydantic schemas for Content API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class SummaryResponse(BaseModel):
    """Summary data for content"""
    overview: str
    key_insights: List[str]
    implications: Optional[str] = None

    class Config:
        from_attributes = True


class ThemeAssociation(BaseModel):
    """Theme association with confidence"""
    theme_id: int
    theme_name: str
    confidence: Optional[float] = None
    color: Optional[str] = None


class ContentResponse(BaseModel):
    """Basic content response for list views"""
    id: int
    title: str
    author: Optional[str] = None
    source_type: str
    source_url: Optional[str] = None
    created_at: datetime

    # Summary preview (first 200 chars of overview)
    summary_preview: Optional[str] = None

    # Associated themes
    themes: List[ThemeAssociation] = []

    class Config:
        from_attributes = True


class ContentDetailResponse(BaseModel):
    """Detailed content response with full summary"""
    id: int
    title: str
    author: Optional[str] = None
    source_type: str
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    publish_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Full summary
    summary: Optional[SummaryResponse] = None

    # Associated themes
    themes: List[ThemeAssociation] = []

    # Metadata
    extraction_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    """Paginated list of content"""
    items: List[ContentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class URLSubmitRequest(BaseModel):
    """Request to submit a URL for processing"""
    url: str = Field(..., description="URL to process (Twitter, arXiv, ACM, or general web)")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://arxiv.org/abs/2301.12345"
            }
        }


class URLSubmitResponse(BaseModel):
    """Response after submitting URL"""
    message: str
    content_id: Optional[int] = None
    job_id: Optional[str] = None
    status: str  # 'processing', 'completed', 'failed'

    # If completed synchronously, include content data
    content: Optional[ContentDetailResponse] = None


class FileUploadResponse(BaseModel):
    """Response after uploading file"""
    message: str
    content_id: Optional[int] = None
    job_id: Optional[str] = None
    status: str

    # If completed synchronously, include content data
    content: Optional[ContentDetailResponse] = None
