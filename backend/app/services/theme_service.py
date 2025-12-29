"""
Theme categorization service.

Handles automatic theme detection and assignment using semantic similarity.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models import Theme, ContentTheme
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

# Pre-defined theme colors
THEME_COLORS = [
    '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF33F3',
    '#33FFF3', '#F3FF33', '#FF8C33', '#8C33FF', '#33FF8C',
    '#FF3383', '#33FFA5', '#A533FF', '#FFA533', '#5733FF',
]


class ThemeService:
    """
    Service for theme categorization and management.
    """

    CONFIDENCE_HIGH = 0.75  # Auto-assign threshold
    CONFIDENCE_LOW = 0.5    # Minimum threshold
    BOOTSTRAP_COUNT = 10    # Number of items before bootstrapping themes

    async def categorize_content(
        self,
        content_id: int,
        summary: Dict[str, Any],
        db: AsyncSession
    ) -> List[int]:
        """
        Categorize content into themes.

        Args:
            content_id: ID of the content
            summary: Summary dict with overview, key_insights, implications
            db: Database session

        Returns:
            list: List of theme IDs assigned to the content

        Raises:
            Exception: If categorization fails
        """
        try:
            # Get existing themes
            result = await db.execute(select(Theme))
            existing_themes = result.scalars().all()

            # Check if we need to bootstrap themes
            if len(existing_themes) < 5:
                # Count total content
                count_result = await db.execute(
                    select(func.count()).select_from(ContentTheme)
                )
                content_count = count_result.scalar()

                # Bootstrap if we have enough content but few themes
                if content_count >= self.BOOTSTRAP_COUNT:
                    logger.info("Bootstrapping themes from existing content...")
                    await self._bootstrap_themes(db)
                    # Re-fetch themes after bootstrapping
                    result = await db.execute(select(Theme))
                    existing_themes = result.scalars().all()

            assigned_theme_ids = []

            if not existing_themes:
                # No themes yet - use suggested themes from summary
                suggested_themes = summary.get('suggested_themes', [])
                for theme_name in suggested_themes[:3]:  # Limit to 3
                    theme = await self._create_theme(theme_name, None, db)
                    assigned_theme_ids.append(theme.id)

                    # Create association
                    content_theme = ContentTheme(
                        content_id=content_id,
                        theme_id=theme.id,
                        confidence=1.0  # New theme, full confidence
                    )
                    db.add(content_theme)

                logger.info(f"Created {len(assigned_theme_ids)} new themes from suggestions")

            else:
                # Categorize using Claude
                themes_data = [
                    {
                        'id': theme.id,
                        'name': theme.name,
                        'description': theme.description
                    }
                    for theme in existing_themes
                ]

                categorization = await ai_service.categorize_content(summary, themes_data)

                # Process theme matches
                for match in categorization.get('theme_matches', []):
                    theme_id = match.get('theme_id')
                    confidence = match.get('confidence', 0)

                    if confidence >= self.CONFIDENCE_LOW and theme_id:
                        # Create association
                        content_theme = ContentTheme(
                            content_id=content_id,
                            theme_id=theme_id,
                            confidence=confidence
                        )
                        db.add(content_theme)
                        assigned_theme_ids.append(theme_id)

                        # Update theme content count
                        await db.execute(
                            update(Theme)
                            .where(Theme.id == theme_id)
                            .values(content_count=Theme.content_count + 1)
                        )

                # Handle new theme suggestion
                new_theme_suggestion = categorization.get('new_theme_suggestion')
                if new_theme_suggestion and len(assigned_theme_ids) == 0:
                    # Only create new theme if no existing themes matched
                    theme = await self._create_theme(
                        new_theme_suggestion['name'],
                        new_theme_suggestion.get('description'),
                        db
                    )
                    assigned_theme_ids.append(theme.id)

                    content_theme = ContentTheme(
                        content_id=content_id,
                        theme_id=theme.id,
                        confidence=0.9  # High confidence for new theme
                    )
                    db.add(content_theme)

                    logger.info(f"Created new theme: {theme.name}")

            await db.flush()
            return assigned_theme_ids

        except Exception as e:
            logger.error(f"Error categorizing content {content_id}: {str(e)}")
            # Don't raise - categorization failure shouldn't block content creation
            return []

    async def _create_theme(
        self,
        name: str,
        description: Optional[str],
        db: AsyncSession
    ) -> Theme:
        """
        Create a new theme.

        Args:
            name: Theme name
            description: Theme description (optional)
            db: Database session

        Returns:
            Theme: Created theme
        """
        # Assign a random color
        color = random.choice(THEME_COLORS)

        theme = Theme(
            name=name,
            description=description,
            color=color,
            content_count=1
        )

        db.add(theme)
        await db.flush()

        logger.info(f"Created theme: {name} (ID: {theme.id})")
        return theme

    async def _bootstrap_themes(self, db: AsyncSession):
        """
        Bootstrap initial themes from existing content summaries.

        Args:
            db: Database session
        """
        try:
            from app.models import Summary

            # Get recent summaries
            result = await db.execute(
                select(Summary).order_by(Summary.generated_at.desc()).limit(20)
            )
            summaries = result.scalars().all()

            if not summaries:
                return

            # Format summaries for Claude
            summary_data = [
                {
                    'overview': s.overview,
                    'key_insights': s.key_insights,
                    'implications': s.implications
                }
                for s in summaries
            ]

            # Generate themes using Claude
            themes = await ai_service.bootstrap_themes(summary_data)

            # Create themes in database
            for theme_data in themes:
                theme = await self._create_theme(
                    theme_data['name'],
                    theme_data.get('description'),
                    db
                )

            await db.flush()
            logger.info(f"Bootstrapped {len(themes)} themes")

        except Exception as e:
            logger.error(f"Error bootstrapping themes: {str(e)}")
            # Don't raise - bootstrap failure is not critical

    async def get_all_themes(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get all themes with metadata.

        Args:
            db: Database session

        Returns:
            list: List of theme dicts
        """
        result = await db.execute(
            select(Theme).order_by(Theme.content_count.desc())
        )
        themes = result.scalars().all()

        return [
            {
                'id': theme.id,
                'name': theme.name,
                'description': theme.description,
                'color': theme.color,
                'content_count': theme.content_count,
                'created_at': theme.created_at.isoformat() if theme.created_at else None,
            }
            for theme in themes
        ]


# Global theme service instance
theme_service = ThemeService()
