"""
API routes for search functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.schemas.search import SearchResponse
from app.schemas.content import ContentResponse, ThemeAssociation
from app.models import Content, Summary, ContentTheme, Theme
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_content(
    q: Optional[str] = Query(None, description="Search query"),
    theme_ids: Optional[str] = Query(None, description="Comma-separated theme IDs"),
    source_types: Optional[str] = Query(None, description="Comma-separated source types"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search content with filters.

    Supports:
    - Full-text search across title and content
    - Filter by themes
    - Filter by source types
    - Filter by date range
    - Pagination
    """
    try:
        # Build base query
        query = select(Content).distinct()

        # Apply search query
        if q:
            search_term = f"%{q}%"
            query = query.where(
                or_(
                    Content.title.ilike(search_term),
                    Content.raw_content.ilike(search_term),
                    Content.author.ilike(search_term)
                )
            )

        # Apply theme filter
        if theme_ids:
            try:
                theme_id_list = [int(tid.strip()) for tid in theme_ids.split(',')]
                query = query.join(ContentTheme).where(ContentTheme.theme_id.in_(theme_id_list))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid theme_ids format. Must be comma-separated integers."
                )

        # Apply source type filter
        if source_types:
            source_type_list = [st.strip() for st in source_types.split(',')]
            query = query.where(Content.source_type.in_(source_type_list))

        # Apply date filters
        if date_from:
            query = query.where(Content.created_at >= date_from)
        if date_to:
            query = query.where(Content.created_at <= date_to)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply ordering and pagination
        query = query.order_by(Content.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await db.execute(query)
        contents = result.scalars().all()

        # Build response items
        items = []
        for content in contents:
            # Get summary preview
            summary_result = await db.execute(
                select(Summary).where(Summary.content_id == content.id)
            )
            summary = summary_result.scalar_one_or_none()
            summary_preview = summary.overview[:200] + "..." if summary and len(summary.overview) > 200 else (summary.overview if summary else None)

            # Get themes
            themes = await _get_content_themes(content.id, db)

            items.append(ContentResponse(
                id=content.id,
                title=content.title,
                author=content.author,
                source_type=content.source_type,
                source_url=content.source_url,
                created_at=content.created_at,
                summary_preview=summary_preview,
                themes=themes
            ))

        total_pages = (total + page_size - 1) // page_size

        return SearchResponse(
            query=q,
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# Helper functions

async def _get_content_themes(content_id: int, db: AsyncSession) -> List[ThemeAssociation]:
    """Get themes associated with content."""
    result = await db.execute(
        select(ContentTheme, Theme)
        .join(Theme)
        .where(ContentTheme.content_id == content_id)
    )
    rows = result.all()

    return [
        ThemeAssociation(
            theme_id=ct.theme_id,
            theme_name=theme.name,
            confidence=ct.confidence,
            color=theme.color
        )
        for ct, theme in rows
    ]
