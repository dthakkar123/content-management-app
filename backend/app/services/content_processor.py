"""
Content processing pipeline orchestrator.

Coordinates extraction → summarization → categorization → storage.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.extractors.factory import extractor_factory
from app.services.ai_service import ai_service
from app.services.theme_service import theme_service
from app.models import Content, Summary, ContentTheme
from app.utils.file_handler import generate_content_hash
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentProcessor:
    """
    Orchestrates the full content processing pipeline.
    """

    async def process_url(
        self,
        url: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a URL: extract → summarize → categorize → store.

        Args:
            url: URL to process
            db: Database session

        Returns:
            dict: Processed content data with content_id, summary, themes

        Raises:
            Exception: If processing fails
        """
        try:
            logger.info(f"Processing URL: {url}")

            # Step 1: Extract content
            extracted = await extractor_factory.extract(url, is_file=False)
            logger.info(f"Extracted content: {extracted['title'][:100]}")

            # Step 2: Check for duplicates
            content_hash = generate_content_hash(
                extracted['content'],
                {'url': url, 'title': extracted['title']}
            )

            existing = await db.execute(
                select(Content).where(Content.content_hash == content_hash)
            )
            existing_content = existing.scalar_one_or_none()

            if existing_content:
                logger.info(f"Content already exists with ID: {existing_content.id}")
                # Return existing content
                return await self._get_content_details(existing_content.id, db)

            # Step 3: Create Content record
            extractor = await extractor_factory.get_extractor(url, is_file=False)
            source_type = extractor.get_source_type()

            content = Content(
                source_type=source_type,
                source_url=url,
                title=extracted['title'],
                author=extracted.get('author'),
                publish_date=extracted.get('publish_date'),
                raw_content=extracted['content'],
                content_hash=content_hash,
                extraction_metadata=extracted.get('metadata', {}),
            )

            db.add(content)
            await db.flush()  # Get the content ID
            logger.info(f"Created content record with ID: {content.id}")

            # Step 4: Generate summary
            summary_data = await ai_service.generate_summary(
                content=extracted['content'],
                metadata={
                    'title': extracted['title'],
                    'author': extracted.get('author'),
                    'source_type': source_type,
                }
            )

            summary = Summary(
                content_id=content.id,
                overview=summary_data['overview'],
                key_insights=summary_data.get('key_insights', []),
                implications=summary_data.get('implications'),
                model_version=summary_data.get('model_version'),
                token_count=summary_data.get('token_count'),
            )

            db.add(summary)
            await db.flush()
            logger.info(f"Generated summary for content {content.id}")

            # Step 5: Categorize into themes
            theme_ids = await theme_service.categorize_content(
                content_id=content.id,
                summary=summary_data,
                db=db
            )
            logger.info(f"Categorized into {len(theme_ids)} themes")

            # Commit transaction
            await db.commit()
            await db.refresh(content)

            return await self._get_content_details(content.id, db)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing URL {url}: {str(e)}")
            raise Exception(f"Failed to process URL: {str(e)}")

    async def process_file(
        self,
        file_path: str,
        original_filename: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a file (PDF): extract → summarize → categorize → store.

        Args:
            file_path: Path to uploaded file
            original_filename: Original filename
            db: Database session

        Returns:
            dict: Processed content data

        Raises:
            Exception: If processing fails
        """
        try:
            logger.info(f"Processing file: {original_filename}")

            # Step 1: Extract content
            extracted = await extractor_factory.extract(file_path, is_file=True)
            logger.info(f"Extracted content from file: {extracted['title'][:100]}")

            # Step 2: Check for duplicates
            content_hash = generate_content_hash(
                extracted['content'],
                {'file': original_filename, 'title': extracted['title']}
            )

            existing = await db.execute(
                select(Content).where(Content.content_hash == content_hash)
            )
            existing_content = existing.scalar_one_or_none()

            if existing_content:
                logger.info(f"Content already exists with ID: {existing_content.id}")
                return await self._get_content_details(existing_content.id, db)

            # Step 3: Create Content record
            extractor = await extractor_factory.get_extractor(file_path, is_file=True)
            source_type = extractor.get_source_type()

            content = Content(
                source_type=source_type,
                file_path=file_path,
                title=extracted['title'],
                author=extracted.get('author'),
                publish_date=extracted.get('publish_date'),
                raw_content=extracted['content'],
                content_hash=content_hash,
                extraction_metadata=extracted.get('metadata', {}),
            )

            db.add(content)
            await db.flush()
            logger.info(f"Created content record with ID: {content.id}")

            # Step 4: Generate summary
            summary_data = await ai_service.generate_summary(
                content=extracted['content'],
                metadata={
                    'title': extracted['title'],
                    'author': extracted.get('author'),
                    'source_type': source_type,
                }
            )

            summary = Summary(
                content_id=content.id,
                overview=summary_data['overview'],
                key_insights=summary_data.get('key_insights', []),
                implications=summary_data.get('implications'),
                model_version=summary_data.get('model_version'),
                token_count=summary_data.get('token_count'),
            )

            db.add(summary)
            await db.flush()
            logger.info(f"Generated summary for content {content.id}")

            # Step 5: Categorize into themes
            theme_ids = await theme_service.categorize_content(
                content_id=content.id,
                summary=summary_data,
                db=db
            )
            logger.info(f"Categorized into {len(theme_ids)} themes")

            # Commit transaction
            await db.commit()
            await db.refresh(content)

            return await self._get_content_details(content.id, db)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing file {original_filename}: {str(e)}")
            raise Exception(f"Failed to process file: {str(e)}")

    async def _get_content_details(
        self,
        content_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get complete content details including summary and themes.

        Args:
            content_id: Content ID
            db: Database session

        Returns:
            dict: Complete content data
        """
        # Fetch content with relationships
        result = await db.execute(
            select(Content).where(Content.id == content_id)
        )
        content = result.scalar_one()

        # Fetch summary
        summary_result = await db.execute(
            select(Summary).where(Summary.content_id == content_id)
        )
        summary = summary_result.scalar_one_or_none()

        # Fetch themes
        theme_result = await db.execute(
            select(ContentTheme).where(ContentTheme.content_id == content_id)
        )
        content_themes = theme_result.scalars().all()

        return {
            'content_id': content.id,
            'title': content.title,
            'author': content.author,
            'source_type': content.source_type,
            'source_url': content.source_url,
            'created_at': content.created_at.isoformat() if content.created_at else None,
            'summary': {
                'overview': summary.overview if summary else None,
                'key_insights': summary.key_insights if summary else [],
                'implications': summary.implications if summary else None,
            } if summary else None,
            'themes': [
                {
                    'theme_id': ct.theme_id,
                    'confidence': ct.confidence
                }
                for ct in content_themes
            ]
        }


# Global processor instance
content_processor = ContentProcessor()
