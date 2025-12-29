from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseExtractor(ABC):
    """
    Abstract base class for all content extractors.

    Each extractor must implement methods to:
    1. Check if it can handle a given source
    2. Extract content from that source
    3. Return its source type identifier
    """

    @abstractmethod
    async def can_handle(self, source: str, is_file: bool = False) -> bool:
        """
        Check if this extractor can handle the given source.

        Args:
            source: URL string or file path
            is_file: True if source is a file path, False if URL

        Returns:
            bool: True if this extractor can handle the source
        """
        pass

    @abstractmethod
    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from the source.

        Args:
            source: URL string or file path
            **kwargs: Additional arguments (e.g., file object for PDFs)

        Returns:
            dict: Standardized content dictionary with keys:
                - title (str): Content title
                - author (str | None): Author name
                - publish_date (datetime | None): Publication date
                - content (str): Extracted text content
                - metadata (dict): Source-specific metadata

        Raises:
            Exception: If extraction fails
        """
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        """
        Return the source type identifier.

        Returns:
            str: One of: 'twitter', 'pdf', 'arxiv', 'acm', 'web'
        """
        pass

    def _create_result(
        self,
        title: str,
        content: str,
        author: Optional[str] = None,
        publish_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Helper method to create standardized result dictionary.

        Args:
            title: Content title
            content: Extracted text
            author: Author name (optional)
            publish_date: Publication date (optional)
            metadata: Additional metadata (optional)

        Returns:
            dict: Standardized result
        """
        return {
            "title": title,
            "author": author,
            "publish_date": publish_date,
            "content": content,
            "metadata": metadata or {},
        }
