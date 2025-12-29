"""
AI service for Claude API integration.

Handles summarization, categorization, and embeddings.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from anthropic import Anthropic, AsyncAnthropic
from app.config import settings
from app.prompts.summarization import get_summarization_prompt, get_brief_summary_prompt
from app.prompts.categorization import (
    get_theme_categorization_prompt,
    get_theme_bootstrap_prompt
)
from app.utils.rate_limiter import APIRateLimits

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for interacting with Claude API for AI-powered features.
    """

    def __init__(self):
        """Initialize Claude API client."""
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.rate_limiter = APIRateLimits.get_limiter("claude")
        self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5
        self.max_tokens = 4096

    async def generate_summary(
        self,
        content: str,
        metadata: Dict[str, Any],
        summary_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generate a structured summary of content using Claude.

        Args:
            content: The full text content to summarize
            metadata: Dict containing title, author, source_type, etc.
            summary_type: Type of summary ('comprehensive' or 'brief')

        Returns:
            dict: Summary with keys:
                - overview (str)
                - key_insights (list[str])
                - implications (str)
                - suggested_themes (list[str])
                - token_count (int)
                - model_version (str)

        Raises:
            Exception: If API call fails
        """
        await self.rate_limiter.acquire()

        try:
            # Generate prompt
            if summary_type == "brief":
                prompt = get_brief_summary_prompt(content, metadata)
            else:
                prompt = get_summarization_prompt(content, metadata)

            logger.info(f"Generating {summary_type} summary for: {metadata.get('title', 'Untitled')[:100]}")

            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent summaries
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract response text
            response_text = response.content[0].text

            # Parse JSON response for comprehensive summary
            if summary_type == "comprehensive":
                try:
                    # Try to extract JSON from response
                    # Sometimes Claude wraps JSON in markdown code blocks
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        response_text = response_text[json_start:json_end].strip()
                    elif "```" in response_text:
                        json_start = response_text.find("```") + 3
                        json_end = response_text.find("```", json_start)
                        response_text = response_text[json_start:json_end].strip()

                    summary_data = json.loads(response_text)

                    # Validate required fields
                    if 'overview' not in summary_data:
                        raise ValueError("Missing 'overview' in summary")
                    if 'key_insights' not in summary_data:
                        raise ValueError("Missing 'key_insights' in summary")

                    # Add metadata
                    summary_data['token_count'] = response.usage.output_tokens
                    summary_data['model_version'] = self.model

                    logger.info(f"Successfully generated summary with {response.usage.output_tokens} tokens")
                    return summary_data

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Response text: {response_text[:500]}")

                    # Fallback: return structured response from text
                    return {
                        'overview': response_text,
                        'key_insights': ["Summary generation partially failed - see overview"],
                        'implications': None,
                        'suggested_themes': [],
                        'token_count': response.usage.output_tokens,
                        'model_version': self.model,
                    }
            else:
                # Brief summary - just return text
                return {
                    'overview': response_text,
                    'key_insights': [],
                    'implications': None,
                    'suggested_themes': [],
                    'token_count': response.usage.output_tokens,
                    'model_version': self.model,
                }

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}")

    async def categorize_content(
        self,
        summary: Dict[str, Any],
        existing_themes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Categorize content into themes using Claude.

        Args:
            summary: Dict with overview, key_insights, implications
            existing_themes: List of existing themes with id, name, description

        Returns:
            dict: With keys:
                - theme_matches: list of (theme_id, confidence, reasoning) tuples
                - new_theme_suggestion: dict or None

        Raises:
            Exception: If API call fails
        """
        await self.rate_limiter.acquire()

        try:
            prompt = get_theme_categorization_prompt(summary, existing_themes)

            logger.info(f"Categorizing content with {len(existing_themes)} existing themes")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = response.content[0].text

            # Parse JSON response
            try:
                # Extract JSON from markdown if needed
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()

                categorization = json.loads(response_text)

                logger.info(f"Categorization complete: {len(categorization.get('theme_matches', []))} matches")
                return categorization

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse categorization response: {e}")
                # Return empty categorization
                return {
                    'theme_matches': [],
                    'new_theme_suggestion': None
                }

        except Exception as e:
            logger.error(f"Error categorizing content: {str(e)}")
            raise Exception(f"Failed to categorize content: {str(e)}")

    async def bootstrap_themes(
        self,
        summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Generate initial themes from first batch of content.

        Args:
            summaries: List of summary dicts

        Returns:
            list: List of theme dicts with name, description

        Raises:
            Exception: If API call fails
        """
        await self.rate_limiter.acquire()

        try:
            prompt = get_theme_bootstrap_prompt(summaries)

            logger.info(f"Bootstrapping themes from {len(summaries)} summaries")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.5,  # Slightly higher for creative theme generation
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = response.content[0].text

            # Parse JSON response
            try:
                # Extract JSON from markdown if needed
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()

                result = json.loads(response_text)
                themes = result.get('themes', [])

                logger.info(f"Generated {len(themes)} initial themes")
                return themes

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse theme bootstrap response: {e}")
                return []

        except Exception as e:
            logger.error(f"Error bootstrapping themes: {str(e)}")
            raise Exception(f"Failed to bootstrap themes: {str(e)}")


# Global AI service instance
ai_service = AIService()
