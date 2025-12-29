from typing import Optional
from app.extractors.base import BaseExtractor
from app.extractors.twitter import TwitterExtractor
from app.extractors.pdf import PDFExtractor
from app.extractors.arxiv import ArxivExtractor
from app.extractors.acm import ACMExtractor
from app.extractors.web import WebExtractor
import logging

logger = logging.getLogger(__name__)


class ExtractorFactory:
    """
    Factory class to select the appropriate extractor for a given source.

    Maintains a registry of extractors and returns the first one that can handle the source.
    """

    def __init__(self):
        # Order matters! Specialized extractors should come before general ones
        self.extractors: list[BaseExtractor] = [
            TwitterExtractor(),
            ArxivExtractor(),
            ACMExtractor(),
            PDFExtractor(),
            WebExtractor(),  # WebExtractor is the fallback for any HTTP URL
        ]

    async def get_extractor(self, source: str, is_file: bool = False) -> BaseExtractor:
        """
        Get the appropriate extractor for a given source.

        Args:
            source: URL string or file path
            is_file: True if source is a file path, False if URL

        Returns:
            BaseExtractor: The extractor that can handle the source

        Raises:
            ValueError: If no suitable extractor is found
        """
        for extractor in self.extractors:
            try:
                if await extractor.can_handle(source, is_file):
                    logger.info(f"Selected {extractor.__class__.__name__} for source: {source[:100]}")
                    return extractor
            except Exception as e:
                logger.warning(f"Error checking if {extractor.__class__.__name__} can handle source: {e}")
                continue

        raise ValueError(f"No suitable extractor found for source: {source[:100]}")

    async def extract(self, source: str, is_file: bool = False, **kwargs) -> dict:
        """
        Convenience method to get extractor and extract content in one call.

        Args:
            source: URL string or file path
            is_file: True if source is a file path, False if URL
            **kwargs: Additional arguments to pass to the extractor

        Returns:
            dict: Extracted content

        Raises:
            ValueError: If no suitable extractor is found
            Exception: If extraction fails
        """
        extractor = await self.get_extractor(source, is_file)
        return await extractor.extract(source, **kwargs)


# Global factory instance
extractor_factory = ExtractorFactory()
