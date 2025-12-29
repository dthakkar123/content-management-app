import arxiv
from typing import Dict, Any
from datetime import datetime
from app.extractors.base import BaseExtractor
from app.utils.rate_limiter import APIRateLimits
from app.utils.url_parser import detect_content_type
import logging

logger = logging.getLogger(__name__)


class ArxivExtractor(BaseExtractor):
    """
    Extractor for arXiv research papers.

    Uses the arxiv Python library to fetch paper metadata and abstract.
    """

    def __init__(self):
        self.rate_limiter = APIRateLimits.get_limiter("arxiv")

    async def can_handle(self, source: str, is_file: bool = False) -> bool:
        """
        Can handle arXiv URLs.

        Args:
            source: URL string
            is_file: False (arXiv extractor doesn't handle files)

        Returns:
            bool: True if source is an arXiv URL
        """
        if is_file:
            return False

        content_type, _ = detect_content_type(source)
        return content_type == 'arxiv'

    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from an arXiv paper.

        Args:
            source: arXiv URL
            **kwargs: Additional arguments (unused)

        Returns:
            dict: Extracted content

        Raises:
            Exception: If extraction fails
        """
        await self.rate_limiter.acquire()

        try:
            # Extract arXiv ID from URL
            _, arxiv_id = detect_content_type(source)

            if not arxiv_id:
                raise ValueError("Could not extract arXiv ID from URL")

            # Fetch paper metadata using arxiv library
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results(), None)

            if not paper:
                raise ValueError(f"Paper not found: {arxiv_id}")

            # Build content from abstract and metadata
            content_parts = [
                f"Abstract:\n{paper.summary}",
                f"\nCategories: {', '.join(paper.categories)}",
            ]

            if paper.comment:
                content_parts.append(f"\nComments: {paper.comment}")

            if paper.journal_ref:
                content_parts.append(f"\nJournal Reference: {paper.journal_ref}")

            if paper.doi:
                content_parts.append(f"\nDOI: {paper.doi}")

            full_content = '\n'.join(content_parts)

            # Get authors
            authors = [author.name for author in paper.authors]
            author_str = ', '.join(authors) if authors else None

            # Published date
            publish_date = paper.published

            return self._create_result(
                title=paper.title,
                content=full_content,
                author=author_str,
                publish_date=publish_date,
                metadata={
                    'url': source,
                    'arxiv_id': arxiv_id,
                    'extractor': 'arxiv',
                    'categories': paper.categories,
                    'primary_category': paper.primary_category,
                    'doi': paper.doi,
                    'journal_ref': paper.journal_ref,
                    'pdf_url': paper.pdf_url,
                    'updated': paper.updated.isoformat() if paper.updated else None,
                }
            )

        except Exception as e:
            logger.error(f"Error extracting arXiv paper {source}: {str(e)}")
            raise Exception(f"Failed to extract arXiv paper: {str(e)}")

    def get_source_type(self) -> str:
        """Return source type identifier."""
        return 'arxiv'
