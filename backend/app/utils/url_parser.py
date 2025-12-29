import re
from urllib.parse import urlparse
from typing import Optional, Tuple


def detect_content_type(url: str) -> Tuple[str, Optional[str]]:
    """
    Detect content type from URL.

    Args:
        url: URL string to analyze

    Returns:
        tuple: (content_type, specific_id)
            - content_type: One of 'twitter', 'arxiv', 'acm', 'web'
            - specific_id: Extracted ID (e.g., arXiv ID, tweet ID) or None
    """
    parsed = urlparse(url.lower())
    domain = parsed.netloc

    # Twitter
    if 'twitter.com' in domain or 'x.com' in domain:
        # Extract tweet ID from URL
        match = re.search(r'/status/(\d+)', url)
        tweet_id = match.group(1) if match else None
        return 'twitter', tweet_id

    # arXiv
    if 'arxiv.org' in domain:
        # Extract arXiv ID (e.g., 2301.12345 or cs/0501001)
        match = re.search(r'arxiv\.org/(abs|pdf)/([a-z\-]+/\d+|\d+\.\d+)', url, re.IGNORECASE)
        arxiv_id = match.group(2) if match else None
        return 'arxiv', arxiv_id

    # ACM Digital Library
    if 'dl.acm.org' in domain or 'acm.org' in domain:
        # Extract DOI or paper ID
        match = re.search(r'doi/([\d\.]+/\d+)', url)
        if match:
            doi = match.group(1)
            return 'acm', doi
        match = re.search(r'/(\d+)$', parsed.path)
        paper_id = match.group(1) if match else None
        return 'acm', paper_id

    # Default to general web
    return 'web', None


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: String to validate

    Returns:
        bool: True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL to a standard format.

    Args:
        url: URL to normalize

    Returns:
        str: Normalized URL
    """
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Parse and reconstruct
    parsed = urlparse(url)

    # Remove trailing slash from path
    path = parsed.path.rstrip('/')

    # Remove fragment
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.

    Args:
        url: URL string

    Returns:
        str: Domain name
    """
    parsed = urlparse(url)
    return parsed.netloc or url
