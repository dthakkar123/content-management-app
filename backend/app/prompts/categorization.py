"""
Prompt templates for theme categorization using Claude API.
"""


def get_theme_categorization_prompt(summary: dict, existing_themes: list) -> str:
    """
    Generate a prompt for categorizing content into themes.

    Args:
        summary: Dict with overview, key_insights, implications
        existing_themes: List of dicts with theme id, name, and description

    Returns:
        str: Formatted prompt for Claude
    """
    # Format existing themes
    themes_text = "\n".join([
        f"{i+1}. {theme['name']}: {theme.get('description', 'No description')}"
        for i, theme in enumerate(existing_themes)
    ])

    if not themes_text:
        themes_text = "No existing themes yet."

    prompt = f"""You are categorizing content into research themes. Given a content summary and existing themes, determine which themes this content belongs to.

**Content Summary:**
Overview: {summary.get('overview', '')}

Key Insights:
{chr(10).join(f"- {insight}" for insight in summary.get('key_insights', []))}

Implications: {summary.get('implications', '')}

**Existing Themes:**
{themes_text}

**Task:**
1. Identify which existing themes (if any) this content belongs to
2. For each match, provide a confidence score (0.0 to 1.0)
3. If this content introduces a significantly new topic not well-covered by existing themes, suggest a new theme

**Output JSON format:**
{{
    "theme_matches": [
        {{
            "theme_id": 1,
            "confidence": 0.85,
            "reasoning": "Brief explanation of why this theme fits"
        }}
    ],
    "new_theme_suggestion": {{
        "name": "Theme Name",
        "description": "Brief description of the new theme",
        "reasoning": "Why this deserves to be a new theme"
    }} or null
}}

**Guidelines:**
- Only match themes with confidence > 0.5
- Content can belong to multiple themes
- Suggest a new theme only if the content is substantially different from existing themes (>30% new)
- New themes should be broad enough to encompass multiple pieces of content, not specific to one article"""

    return prompt


def get_theme_bootstrap_prompt(summaries: list) -> str:
    """
    Generate a prompt to bootstrap initial themes from first batch of content.

    Args:
        summaries: List of summary dicts (overview, key_insights, implications)

    Returns:
        str: Formatted prompt for Claude
    """
    summaries_text = "\n\n".join([
        f"Summary {i+1}:\nOverview: {s.get('overview', '')}\nKey Insights: {', '.join(s.get('key_insights', []))}"
        for i, s in enumerate(summaries)
    ])

    prompt = f"""You are analyzing the first batch of content summaries to identify broad research themes that will be used to categorize future content.

**Content Summaries:**
{summaries_text}

**Task:**
Identify 5-8 broad, high-level research themes that emerge from these summaries. These themes should:
1. Be broad enough to encompass multiple pieces of content
2. Be distinct from each other
3. Cover the major topics represented in the summaries
4. Be useful for organizing and discovering related content

**Output JSON format:**
{{
    "themes": [
        {{
            "name": "Theme Name (2-4 words)",
            "description": "A clear description of what this theme encompasses (1-2 sentences)",
            "example_content": ["Brief reference to which summaries fit this theme"]
        }}
    ]
}}

**Examples of good themes:**
- "Machine Learning & AI"
- "Climate Science & Policy"
- "Healthcare Innovation"
- "Social Media & Digital Culture"
- "Quantum Computing"

**Examples of bad themes (too specific):**
- "GPT-4 Architecture" (too narrow)
- "Temperature in California" (too narrow)
- "This specific paper's findings" (too narrow)"""

    return prompt
