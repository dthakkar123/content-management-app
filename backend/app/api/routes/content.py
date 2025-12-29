"""
API routes for content operations.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Optional
from app.database import get_db
from app.schemas.content import (
    ContentResponse,
    ContentListResponse,
    ContentDetailResponse,
    URLSubmitRequest,
    URLSubmitResponse,
    FileUploadResponse,
    SummaryResponse,
    ThemeAssociation,
)
from app.models import Content, Summary, ContentTheme, Theme
from app.services.content_processor import content_processor
from app.utils.file_handler import save_upload_file, is_allowed_file_type, delete_file
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/content/url", response_model=URLSubmitResponse, status_code=status.HTTP_201_CREATED)
async def submit_url(
    request: URLSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a URL for processing.

    Supports:
    - Twitter/X threads
    - arXiv papers
    - ACM Digital Library
    - General web articles
    """
    try:
        logger.info(f"Received URL submission: {request.url}")

        # Process the URL (synchronously for now)
        result = await content_processor.process_url(request.url, db)

        # Fetch full content details
        content = await _get_content_detail(result['content_id'], db)

        return URLSubmitResponse(
            message="URL processed successfully",
            content_id=result['content_id'],
            status="completed",
            content=content
        )

    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process URL: {str(e)}"
        )


@router.post("/content/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PDF file for processing.
    """
    try:
        logger.info(f"Received file upload: {file.filename}")

        # Validate file type
        if not is_allowed_file_type(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )

        # Save file
        file_path = await save_upload_file(file)
        logger.info(f"File saved to: {file_path}")

        # Process the file
        result = await content_processor.process_file(file_path, file.filename, db)

        # Fetch full content details
        content = await _get_content_detail(result['content_id'], db)

        return FileUploadResponse(
            message="File processed successfully",
            content_id=result['content_id'],
            status="completed",
            content=content
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


@router.get("/content", response_model=ContentListResponse)
async def list_content(
    page: int = 1,
    page_size: int = 10,
    source_type: Optional[str] = None,
    theme_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List content with pagination and optional filters.

    Args:
        page: Page number (starts at 1)
        page_size: Items per page (max 100)
        source_type: Filter by source type (twitter, pdf, arxiv, acm, web)
        theme_id: Filter by theme ID
    """
    try:
        # Validate pagination
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

        # Build query
        query = select(Content)

        # Apply filters
        if source_type:
            query = query.where(Content.source_type == source_type)

        if theme_id:
            query = query.join(ContentTheme).where(ContentTheme.theme_id == theme_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
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

        return ContentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list content: {str(e)}"
        )


@router.get("/content/{content_id}", response_model=ContentDetailResponse)
async def get_content(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific content item.
    """
    try:
        content = await _get_content_detail(content_id, db)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content {content_id} not found"
            )
        return content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching content {content_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch content: {str(e)}"
        )


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a content item and its associated data.
    """
    try:
        # Check if content exists
        result = await db.execute(
            select(Content).where(Content.id == content_id)
        )
        content = result.scalar_one_or_none()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content {content_id} not found"
            )

        # Delete associated file if exists
        if content.file_path:
            await delete_file(content.file_path)

        # Delete content (cascade will handle summary and themes)
        await db.execute(
            delete(Content).where(Content.id == content_id)
        )
        await db.commit()

        logger.info(f"Deleted content {content_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting content {content_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete content: {str(e)}"
        )


# Helper functions

async def _get_content_detail(content_id: int, db: AsyncSession) -> Optional[ContentDetailResponse]:
    """Get detailed content information."""
    # Fetch content
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        return None

    # Fetch summary
    summary_result = await db.execute(
        select(Summary).where(Summary.content_id == content_id)
    )
    summary = summary_result.scalar_one_or_none()

    # Get themes
    themes = await _get_content_themes(content_id, db)

    return ContentDetailResponse(
        id=content.id,
        title=content.title,
        author=content.author,
        source_type=content.source_type,
        source_url=content.source_url,
        file_path=content.file_path,
        publish_date=content.publish_date,
        created_at=content.created_at,
        updated_at=content.updated_at,
        summary=SummaryResponse(
            overview=summary.overview,
            key_insights=summary.key_insights,
            implications=summary.implications
        ) if summary else None,
        themes=themes,
        extraction_metadata=content.extraction_metadata
    )


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
