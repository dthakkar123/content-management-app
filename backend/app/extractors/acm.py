import aiohttp
from typing import Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from app.extractors.base import BaseExtractor
from app.utils.rate_limiter import APIRateLimits
from app.utils.url_parser import detect_content_type
import logging

logger = logging.getLogger(__name__)


class ACMExtractor(BaseExtractor):
    """
    Extractor for ACM Digital Library papers.

    Uses web scraping to extract paper metadata and abstract.
    """

    def __init__(self):
        self.rate_limiter = APIRateLimits.get_limiter("general")

    async def can_handle(self, source: str, is_file: bool = False) -> bool:
        """
        Can handle ACM Digital Library URLs.

        Args:
            source: URL string
            is_file: False (ACM extractor doesn't handle files)

        Returns:
            bool: True if source is an ACM URL
        """
        if is_file:
            return False

        content_type, _ = detect_content_type(source)
        return content_type == 'acm'

    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from an ACM Digital Library paper.

        Args:
            source: ACM URL
            **kwargs: Additional arguments (unused)

        Returns:
            dict: Extracted content

        Raises:
            Exception: If extraction fails
        """
        await self.rate_limiter.acquire()

        try:
            # Fetch the page
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(source, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    html = await response.text()

            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = None
            title_elem = (
                soup.find('h1', class_='citation__title') or
                soup.find('h1', {'property': 'name'}) or
                soup.find('meta', {'name': 'dc.Title'})
            )

            if title_elem:
                if title_elem.name == 'meta':
                    title = title_elem.get('content')
                else:
                    title = title_elem.get_text(strip=True)

            if not title:
                # Fallback to page title
                title_tag = soup.find('title')
                title = title_tag.string if title_tag else "Untitled ACM Paper"

            # Extract authors
            authors = []
            author_elems = soup.find_all('span', class_='loa__author-name') or soup.find_all('a', {'class': 'author-name'})

            for author_elem in author_elems:
                author_name = author_elem.get_text(strip=True)
                if author_name:
                    authors.append(author_name)

            author_str = ', '.join(authors) if authors else None

            # Extract abstract
            abstract = None
            abstract_elem = (
                soup.find('div', class_='abstractSection') or
                soup.find('div', {'property': 'description'}) or
                soup.find('meta', {'name': 'description'})
            )

            if abstract_elem:
                if abstract_elem.name == 'meta':
                    abstract = abstract_elem.get('content')
                else:
                    # Get text but skip the "Abstract" heading
                    abstract_text = abstract_elem.get_text(separator='\n', strip=True)
                    if abstract_text.startswith('Abstract'):
                        abstract = abstract_text[8:].strip()
                    else:
                        abstract = abstract_text

            # Extract DOI
            doi = None
            doi_elem = soup.find('meta', {'name': 'dc.Identifier'}) or soup.find('a', class_='issue-item__doi')

            if doi_elem:
                if doi_elem.name == 'meta':
                    doi = doi_elem.get('content')
                else:
                    doi = doi_elem.get_text(strip=True)

            # Extract publication date
            publish_date = None
            date_elem = soup.find('meta', {'name': 'dc.Date'}) or soup.find('span', class_='CitationCoverDate')

            if date_elem:
                try:
                    from dateutil import parser
                    date_str = date_elem.get('content') if date_elem.name == 'meta' else date_elem.get_text(strip=True)
                    publish_date = parser.parse(date_str)
                except Exception:
                    pass

            # Build content
            content_parts = []

            if abstract:
                content_parts.append(f"Abstract:\n{abstract}")

            # Try to extract additional sections
            for section_class in ['abstractSection', 'section', 'article-section']:
                sections = soup.find_all('div', class_=section_class)
                for section in sections[:5]:  # Limit to first 5 sections
                    section_text = section.get_text(separator='\n', strip=True)
                    if section_text and section_text not in content_parts:
                        content_parts.append(section_text)

            if not content_parts:
                content_parts.append("Abstract not available. Please visit the ACM Digital Library for full content.")

            full_content = '\n\n'.join(content_parts)

            return self._create_result(
                title=title,
                content=full_content,
                author=author_str,
                publish_date=publish_date,
                metadata={
                    'url': source,
                    'extractor': 'acm',
                    'doi': doi,
                    'authors_list': authors,
                }
            )

        except Exception as e:
            logger.error(f"Error extracting ACM paper {source}: {str(e)}")
            raise Exception(f"Failed to extract ACM paper: {str(e)}")

    def get_source_type(self) -> str:
        """Return source type identifier."""
        return 'acm'
