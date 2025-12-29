"""
Prompt templates for content summarization using Claude API.
"""


def get_summarization_prompt(content: str, metadata: dict) -> str:
    """
    Generate a prompt for content summarization.

    Args:
        content: The full text content to summarize
        metadata: Dict containing title, author, source_type, etc.

    Returns:
        str: Formatted prompt for Claude
    """
    content_type = metadata.get('source_type', 'content')
    title = metadata.get('title', 'Untitled')
    author = metadata.get('author', 'Unknown')

    prompt = f"""You are an expert research analyst. Analyze the following {content_type} and provide a comprehensive, structured summary.

Content Type: {content_type}
Title: {title}
Author: {author}

Content:
{content}

Please provide a detailed summary in the following JSON format:
{{
    "overview": "A 2-3 paragraph overview explaining the main method, approach, or thesis. Focus on what problem is being addressed and how it's being solved or explored.",
    "key_insights": [
        "First key insight or major finding (be specific and detailed)",
        "Second key insight or major finding",
        "Third key insight or major finding",
        "Add more as needed - aim for 3-5 key insights"
    ],
    "implications": "1-2 paragraphs discussing the broader implications, applications, or significance of this work. What does it mean for the world? How might it influence the field or society? What are the potential applications?",
    "suggested_themes": ["Theme 1", "Theme 2", "Theme 3"]
}}

Guidelines:
1. **Overview**: Explain the core method, approach, or argument clearly. Avoid just restating the title.
2. **Key Insights**: Extract the most important findings, discoveries, or arguments. Be specific with examples or data when available.
3. **Implications**: Think broadly about impact - academic significance, practical applications, societal relevance, future directions.
4. **Suggested Themes**: Identify 2-4 broad research themes or topics this content belongs to (e.g., "Machine Learning", "Climate Change", "Social Media Ethics")

Be thorough and analytical. This summary should give someone a complete understanding of the content's value and significance."""

    return prompt


def get_brief_summary_prompt(content: str, metadata: dict) -> str:
    """
    Generate a prompt for a brief summary (for quick previews).

    Args:
        content: The full text content to summarize
        metadata: Dict containing title, author, source_type, etc.

    Returns:
        str: Formatted prompt for Claude
    """
    title = metadata.get('title', 'Untitled')

    prompt = f"""Provide a concise 2-3 sentence summary of the following content:

Title: {title}

Content:
{content}

Summary:"""

    return prompt
