import tweepy
from typing import Dict, Any
from datetime import datetime
from app.extractors.base import BaseExtractor
from app.utils.rate_limiter import APIRateLimits
from app.utils.url_parser import detect_content_type
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TwitterExtractor(BaseExtractor):
    """
    Extractor for Twitter/X threads and tweets.

    Uses the Twitter API v2 via tweepy to fetch tweet content.
    """

    def __init__(self):
        self.rate_limiter = APIRateLimits.get_limiter("twitter")
        self._client = None

    def _get_client(self):
        """Lazy initialization of Twitter client."""
        if not self._client and settings.TWITTER_BEARER_TOKEN:
            self._client = tweepy.Client(bearer_token=settings.TWITTER_BEARER_TOKEN)
        return self._client

    async def can_handle(self, source: str, is_file: bool = False) -> bool:
        """
        Can handle Twitter/X URLs.

        Args:
            source: URL string
            is_file: False (Twitter extractor doesn't handle files)

        Returns:
            bool: True if source is a Twitter/X URL
        """
        if is_file:
            return False

        content_type, _ = detect_content_type(source)
        return content_type == 'twitter'

    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from a Twitter thread.

        Args:
            source: Twitter URL
            **kwargs: Additional arguments (unused)

        Returns:
            dict: Extracted content

        Raises:
            Exception: If extraction fails
        """
        await self.rate_limiter.acquire()

        try:
            client = self._get_client()

            if not client:
                raise ValueError("Twitter API credentials not configured. Set TWITTER_BEARER_TOKEN in .env")

            # Extract tweet ID from URL
            _, tweet_id = detect_content_type(source)

            if not tweet_id:
                raise ValueError("Could not extract tweet ID from URL")

            # Fetch tweet with expansions and fields
            response = client.get_tweet(
                tweet_id,
                expansions=['author_id', 'referenced_tweets.id'],
                tweet_fields=['created_at', 'author_id', 'conversation_id', 'public_metrics', 'entities'],
                user_fields=['name', 'username', 'verified'],
            )

            if not response.data:
                raise ValueError(f"Tweet not found: {tweet_id}")

            tweet = response.data
            users = {user.id: user for user in response.includes.get('users', [])} if response.includes else {}
            author = users.get(tweet.author_id)

            # Build content starting with main tweet
            content_parts = [tweet.text]

            # Check if this is part of a thread (conversation)
            if tweet.conversation_id and tweet.conversation_id != tweet.id:
                try:
                    # Fetch the conversation thread
                    thread_response = client.search_recent_tweets(
                        query=f"conversation_id:{tweet.conversation_id}",
                        max_results=100,
                        tweet_fields=['created_at', 'author_id'],
                        sort_order='chronological',
                    )

                    if thread_response.data:
                        # Filter tweets by same author and sort chronologically
                        thread_tweets = [
                            t for t in thread_response.data
                            if t.author_id == tweet.author_id
                        ]
                        thread_tweets.sort(key=lambda t: t.created_at)

                        # Add thread tweets to content
                        for t in thread_tweets:
                            if t.id != tweet.id:  # Don't duplicate the main tweet
                                content_parts.append(f"\n---\n{t.text}")

                except Exception as e:
                    logger.warning(f"Could not fetch thread: {str(e)}")

            full_content = '\n'.join(content_parts)

            # Build title
            title = f"Tweet by @{author.username}" if author else "Twitter Thread"
            if author and author.name:
                title = f"Tweet by {author.name} (@{author.username})"

            author_str = f"{author.name} (@{author.username})" if author else None

            return self._create_result(
                title=title,
                content=full_content,
                author=author_str,
                publish_date=tweet.created_at,
                metadata={
                    'url': source,
                    'tweet_id': tweet_id,
                    'extractor': 'twitter',
                    'conversation_id': tweet.conversation_id,
                    'author_username': author.username if author else None,
                    'author_verified': author.verified if author else False,
                    'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else None,
                }
            )

        except Exception as e:
            logger.error(f"Error extracting tweet {source}: {str(e)}")
            raise Exception(f"Failed to extract tweet: {str(e)}")

    def get_source_type(self) -> str:
        """Return source type identifier."""
        return 'twitter'
