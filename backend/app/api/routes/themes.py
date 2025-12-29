"""
API routes for theme management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List
from app.database import get_db
from app.schemas.theme import ThemeResponse, ThemeCreate, ThemeUpdate
from app.schemas.content import ContentResponse, ContentListResponse, ThemeAssociation
from app.models import Theme, ContentTheme, Content, Summary
from app.services.theme_service import theme_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/themes", response_model=List[ThemeResponse])
async def list_themes(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all themes ordered by content count (descending).
    """
    try:
        themes = await theme_service.get_all_themes(db)
        return [ThemeResponse(**theme) for theme in themes]

    except Exception as e:
        logger.error(f"Error listing themes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list themes: {str(e)}"
        )


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific theme by ID.
    """
    try:
        result = await db.execute(
            select(Theme).where(Theme.id == theme_id)
        )
        theme = result.scalar_one_or_none()

        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Theme {theme_id} not found"
            )

        return ThemeResponse(
            id=theme.id,
            name=theme.name,
            description=theme.description,
            color=theme.color,
            content_count=theme.content_count,
            created_at=theme.created_at,
            updated_at=theme.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching theme {theme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch theme: {str(e)}"
        )


@router.get("/themes/{theme_id}/content", response_model=ContentListResponse)
async def get_theme_content(
    theme_id: int,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all content associated with a theme.

    Args:
        theme_id: Theme ID
        page: Page number (starts at 1)
        page_size: Items per page (max 100)
    """
    try:
        # Validate pagination
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

        # Check if theme exists
        theme_result = await db.execute(
            select(Theme).where(Theme.id == theme_id)
        )
        theme = theme_result.scalar_one_or_none()

        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Theme {theme_id} not found"
            )

        # Get total count
        from sqlalchemy import func
        count_result = await db.execute(
            select(func.count())
            .select_from(ContentTheme)
            .where(ContentTheme.theme_id == theme_id)
        )
        total = count_result.scalar()

        # Get content IDs for this theme
        content_theme_result = await db.execute(
            select(ContentTheme)
            .where(ContentTheme.theme_id == theme_id)
            .order_by(ContentTheme.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        content_themes = content_theme_result.scalars().all()

        # Fetch content details
        items = []
        for ct in content_themes:
            content_result = await db.execute(
                select(Content).where(Content.id == ct.content_id)
            )
            content = content_result.scalar_one_or_none()

            if content:
                # Get summary preview
                summary_result = await db.execute(
                    select(Summary).where(Summary.content_id == content.id)
                )
                summary = summary_result.scalar_one_or_none()
                summary_preview = summary.overview[:200] + "..." if summary and len(summary.overview) > 200 else (summary.overview if summary else None)

                # Get all themes for this content
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
        logger.error(f"Error fetching content for theme {theme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch theme content: {str(e)}"
        )


@router.post("/themes", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    theme_data: ThemeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new theme manually.
    """
    try:
        # Check if theme with same name exists
        result = await db.execute(
            select(Theme).where(Theme.name == theme_data.name)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Theme with name '{theme_data.name}' already exists"
            )

        # Create theme
        theme = Theme(
            name=theme_data.name,
            description=theme_data.description,
            color=theme_data.color or "#3B82F6",  # Default blue
            content_count=0
        )

        db.add(theme)
        await db.commit()
        await db.refresh(theme)

        logger.info(f"Created theme: {theme.name} (ID: {theme.id})")

        return ThemeResponse(
            id=theme.id,
            name=theme.name,
            description=theme.description,
            color=theme.color,
            content_count=theme.content_count,
            created_at=theme.created_at,
            updated_at=theme.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating theme: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create theme: {str(e)}"
        )


@router.put("/themes/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: int,
    theme_data: ThemeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a theme's properties.
    """
    try:
        # Check if theme exists
        result = await db.execute(
            select(Theme).where(Theme.id == theme_id)
        )
        theme = result.scalar_one_or_none()

        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Theme {theme_id} not found"
            )

        # Update fields
        update_data = theme_data.model_dump(exclude_unset=True)

        if update_data:
            await db.execute(
                update(Theme)
                .where(Theme.id == theme_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(theme)

        logger.info(f"Updated theme {theme_id}")

        return ThemeResponse(
            id=theme.id,
            name=theme.name,
            description=theme.description,
            color=theme.color,
            content_count=theme.content_count,
            created_at=theme.created_at,
            updated_at=theme.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating theme {theme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update theme: {str(e)}"
        )


@router.delete("/themes/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a theme.

    Note: This will remove the theme association from all content,
    but won't delete the content itself.
    """
    try:
        # Check if theme exists
        result = await db.execute(
            select(Theme).where(Theme.id == theme_id)
        )
        theme = result.scalar_one_or_none()

        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Theme {theme_id} not found"
            )

        # Delete theme (cascade will handle content_themes)
        await db.execute(
            delete(Theme).where(Theme.id == theme_id)
        )
        await db.commit()

        logger.info(f"Deleted theme {theme_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting theme {theme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete theme: {str(e)}"
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
