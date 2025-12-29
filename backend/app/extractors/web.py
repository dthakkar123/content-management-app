import aiohttp
import ssl
import certifi
from typing import Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import trafilatura
from app.extractors.base import BaseExtractor
from app.utils.rate_limiter import APIRateLimits
import logging

logger = logging.getLogger(__name__)


class WebExtractor(BaseExtractor):
    """
    Extractor for general web articles and blog posts.

    Uses trafilatura for robust content extraction and BeautifulSoup as fallback.
    """

    def __init__(self):
        self.rate_limiter = APIRateLimits.get_limiter("general")

    async def can_handle(self, source: str, is_file: bool = False) -> bool:
        """
        Can handle any HTTP/HTTPS URL that's not handled by specialized extractors.

        Args:
            source: URL string
            is_file: False (web extractor doesn't handle files)

        Returns:
            bool: True if source is a valid URL
        """
        if is_file:
            return False

        # Web extractor acts as fallback for any HTTP/HTTPS URL
        return source.startswith(('http://', 'https://'))

    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from a web page.

        Args:
            source: URL to extract from
            **kwargs: Additional arguments (unused)

        Returns:
            dict: Extracted content

        Raises:
            Exception: If extraction fails
        """
        await self.rate_limiter.acquire()

        try:
            # Create SSL context with certifi certificates
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            # Fetch the page
            async with aiohttp.ClientSession() as session:
                async with session.get(source, ssl=ssl_context, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    # Handle different encodings gracefully
                    try:
                        html = await response.text()
                    except UnicodeDecodeError:
                        # If UTF-8 fails, read as bytes and decode with error handling
                        content_bytes = await response.read()
                        html = content_bytes.decode('utf-8', errors='ignore')

            # Try trafilatura first (best for articles)
            extracted = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                include_links=False,
            )

            if extracted:
                # Extract metadata
                metadata_dict = trafilatura.extract_metadata(html)

                title = metadata_dict.title if metadata_dict else None
                author = metadata_dict.author if metadata_dict else None
                publish_date = None

                if metadata_dict and metadata_dict.date:
                    try:
                        # Try to parse the date
                        from dateutil import parser
                        publish_date = parser.parse(metadata_dict.date)
                    except Exception:
                        pass

                # If trafilatura didn't get title, use BeautifulSoup
                if not title:
                    soup = BeautifulSoup(html, 'lxml')
                    title_tag = soup.find('title')
                    title = title_tag.string if title_tag else "Untitled"

                return self._create_result(
                    title=title or "Untitled",
                    content=extracted,
                    author=author,
                    publish_date=publish_date,
                    metadata={
                        'url': source,
                        'extractor': 'web',
                        'extraction_method': 'trafilatura',
                    }
                )

            # Fallback to BeautifulSoup if trafilatura fails
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = soup.find('title')
            title_text = title.string if title else "Untitled"

            # Try to find main content
            main_content = None

            # Common content selectors
            for selector in ['article', 'main', '.post-content', '.article-content', '.entry-content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text(separator='\n', strip=True)
                    break

            # Fallback to body if no main content found
            if not main_content:
                body = soup.find('body')
                if body:
                    # Remove script and style tags
                    for tag in body(['script', 'style', 'nav', 'header', 'footer']):
                        tag.decompose()
                    main_content = body.get_text(separator='\n', strip=True)

            if not main_content:
                raise ValueError("Could not extract content from page")

            # Try to extract author from meta tags
            author = None
            author_meta = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'author'})
            if author_meta:
                author = author_meta.get('content')

            return self._create_result(
                title=title_text,
                content=main_content,
                author=author,
                publish_date=None,
                metadata={
                    'url': source,
                    'extractor': 'web',
                    'extraction_method': 'beautifulsoup',
                }
            )

        except Exception as e:
            logger.error(f"Error extracting content from {source}: {str(e)}")
            raise Exception(f"Failed to extract content: {str(e)}")

    def get_source_type(self) -> str:
        """Return source type identifier."""
        return 'web'
