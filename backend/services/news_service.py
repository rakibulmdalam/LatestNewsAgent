"""
News service providing dummy articles and formatting them according to
user preferences. In a real system this module would integrate with
third‑party APIs such as Exa for fetching live news and another model
for summarisation and tone adaptation. For this exercise we rely on
local data and optionally call a locally installed `ollama` command
with the Phi3 model to tailor responses. If the `ollama` binary is
unavailable the service falls back to simple string manipulations.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
from typing import Dict, List, Optional

from . import QUESTIONS


# Dummy news database. Each entry has a title, description and a set
# of tags. Feel free to extend this list to provide more variety.
DUMMY_NEWS: List[Dict[str, str]] = [
    {
        "title": "Breakthrough in Quantum Computing",
        "description": "Scientists have achieved a major milestone in quantum computing by demonstrating a 100‑qubit processor.",
        "topics": "technology",
    },
    {
        "title": "Local Team Wins Championship",
        "description": "In an exciting finale, the underdogs clinched the national championship with a last‑minute score.",
        "topics": "sports",
    },
    {
        "title": "New Environmental Policies Introduced",
        "description": "The government has introduced sweeping new policies aimed at reducing carbon emissions by 50% by 2030.",
        "topics": "politics",
    },
    {
        "title": "Advances in Renewable Energy",
        "description": "Researchers have developed a more efficient solar cell that could significantly reduce the cost of renewable energy.",
        "topics": "technology",
    },
    {
        "title": "Historic Peace Agreement Signed",
        "description": "Two neighbouring countries have signed a historic peace agreement, ending decades of conflict.",
        "topics": "politics",
    },
    {
        "title": "Athlete Breaks World Record",
        "description": "A world record was shattered at the international meet, with the athlete setting a new benchmark in track and field.",
        "topics": "sports",
    },
]


def has_ollama() -> bool:
    """Check if the `ollama` binary is available in PATH."""
    return bool(shutil.which("ollama"))


def call_ollama(model: str, prompt: str) -> Optional[str]:
    """Invoke the local ollama model with the provided prompt.

    This function calls `ollama run` with the given model and feeds the
    prompt to standard input. If `ollama` is not available or an
    error occurs, it returns None.
    """
    # Avoid blocking if ollama isn't installed. We use shutil.which to
    # determine availability.
    import shutil
    if not shutil.which("ollama"):
        return None
    try:
        # The command prints the generated text to stdout.
        # We'll read the output and return it as a string. We limit
        # output length to avoid long responses.
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.decode().strip()
    except Exception:
        pass
    return None


def fetch_news(topics: str, count: int = 3) -> List[Dict[str, str]]:
    """Select dummy news items matching the requested topics.

    Args:
        topics: A comma‑separated string of topics (case insensitive).
        count: The number of items to return.

    Returns:
        A list of dictionaries containing the selected news items.
    """
    requested_topics = {t.strip().lower() for t in topics.split(",")}
    # Filter articles that match any of the requested topics. If none
    # match, return random items.
    matches = [item for item in DUMMY_NEWS if item["topics"] in requested_topics]
    if not matches:
        matches = DUMMY_NEWS[:]
    random.shuffle(matches)
    return matches[:count]


def adapt_article(article: Dict[str, str], preferences: Dict[str, str]) -> str:
    """Produce a summary of an article tailored to user preferences.

    This function constructs a prompt to instruct a local model (if
    available) to rewrite the article description according to the
    specified tone, response format, language and interaction style.
    When no local model is available, it falls back to a simple
    template that inserts bullet points or paragraphs as requested.

    Args:
        article: A dictionary with keys 'title', 'description' and
            'topics'.
        preferences: A dictionary of collected user preferences.

    Returns:
        A string containing the adapted summary.
    """
    tone = preferences.get("tone_of_voice", "formal")
    response_format = preferences.get("response_format", "paragraphs")
    language = preferences.get("language", "English")
    interaction_style = preferences.get("interaction_style", "concise")
    title = article["title"]
    description = article["description"]
    topics = article["topics"]
    # Build a prompt instructing the model to summarise and rephrase
    # according to preferences.
    prompt = (
        f"You are a helpful assistant tasked with rewriting news articles.\n"
        f"Please summarise the following news article in {language}.\n"
        f"Use a {tone} tone and make the summary {interaction_style}.\n"
        f"Present the response as {response_format}.\n\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Topics: {topics}\n\n"
        f"Summary:"
    )
    # Try to call the local model. If it fails or returns None,
    # generate a naive summary.
    summary = call_ollama("phi3", prompt)
    if summary:
        return summary
    # Fallback: simple transformation. For bullet points we split the
    # description into clauses.
    if response_format.lower().startswith("bullet"):
        # Insert bullet markers (•) for each sentence.
        sentences = [s.strip() for s in description.split(".") if s.strip()]
        bullets = [f"• {s.strip()}." for s in sentences]
        summary_text = "\n".join(bullets)
    else:
        summary_text = description
    # Apply interaction style. If detailed, we simply include the title.
    if interaction_style.lower().startswith("detailed"):
        summary_text = f"{title}: {summary_text}"
    # Very naive tone adjustment: convert to enthusiastic by adding exclamation.
    if tone.lower().startswith("enthusias"):
        summary_text = summary_text.replace(".", "!")
    # No multilingual support in fallback; assume English.
    return summary_text


def generate_news_response(preferences: Dict[str, str], count: int = 3) -> str:
    """Generate a combined response with multiple news items.

    This returns a formatted string containing the adapted summaries of
    `count` articles based on the user's topic preferences and other
    settings.
    """
    topics = preferences.get("news_topics", "technology")
    articles = fetch_news(topics, count)
    summaries = [adapt_article(article, preferences) for article in articles]
    # Concatenate summaries separated by blank lines for readability.
    return "\n\n".join(summaries)