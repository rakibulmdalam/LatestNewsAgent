"""
Tool implementations for the Latest News Agent.

This module provides two asynchronous functions that the agent can
invoke. They are deliberately kept simple and synchronous when
`MOCK_MODE` is enabled, returning deterministic outputs for
development and testing purposes.

In a real deployment, `exa_news_fetcher` would make an HTTP call
to Exa's API using an API key and return normalised results.
`news_summarizer` would call a language model such as OpenAI's
`gpt-4o` to produce a concise brief honouring the user's
preferences.
"""

from __future__ import annotations

import os
import datetime as dt
from typing import List, Optional

try:
    import httpx  # type: ignore
except ImportError:
    httpx = None  # The environment might not have httpx installed

from .schemas import Article, FetchParams, Preferences


# Determine whether to run in mock mode. When true, network
# requests are skipped and deterministic data is returned instead.
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() in {"1", "true", "yes"}

# Read the Exa API key if present. In this environment it will
# likely be undefined.
EXA_API_KEY = os.getenv("EXA_API_KEY")

# Base URL for Exa's news search API.
EXA_BASE_URL = "https://api.exa.ai"


def _mock_articles(query: str, n: int) -> List[Article]:
    """
    Generate a list of mock articles for development and testing.

    Each article has a predictable title containing the query and a
    monotonically decreasing publication timestamp. URLs are
    synthetic and do not lead to real content. Snippets are kept
    simple.
    """
    now = dt.datetime.utcnow()
    articles: List[Article] = []
    for i in range(n):
        articles.append(
            Article(
                title=f"Mock headline about {query} #{i + 1}",
                url=f"https://example.com/{query.replace(' ', '-')}/{i + 1}",
                snippet="This is a mock snippet for development.",
                published_at=now - dt.timedelta(hours=i * 3),
                source="example.com",
            )
        )
    return articles


async def exa_news_fetcher(params: FetchParams) -> List[Article]:
    """
    Fetch the latest news articles for a given query.

    When `MOCK_MODE` is true or there is no API key, this function
    returns a list of mock articles. Otherwise it attempts to call
    Exa's REST API using `httpx`. If `httpx` is not available or
    a network error occurs, it falls back to mock articles.
    """
    if MOCK_MODE or not EXA_API_KEY:
        return _mock_articles(params.query, params.num_results)

    # If httpx is unavailable, we cannot perform a real HTTP request.
    if httpx is None:
        return _mock_articles(params.query, params.num_results)

    # Build the request payload according to Exa's API specification.
    payload = {
        "query": params.query,
        "type": "news",
        "numResults": params.num_results,
        "recencyDays": params.recency_days,
        "includeDomains": [],
        "useAutoprompt": True,
    }
    headers = {
        "Authorization": f"Bearer {EXA_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{EXA_BASE_URL}/search", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except Exception:
        # On any error, fall back to mock articles. In production you
        # would log the exception and propagate a user friendly error.
        return _mock_articles(params.query, params.num_results)

    # Normalise the response into a list of Article objects. The
    # exact structure depends on Exa's API; here we assume a
    # reasonable schema. Missing fields are handled gracefully.
    out: List[Article] = []
    for item in data.get("results", []):
        try:
            published = item.get("publishedDate")
            published_at = None
            if published:
                published_at = dt.datetime.fromisoformat(published.replace("Z", "+00:00"))
            out.append(
                Article(
                    title=item.get("title", "Untitled"),
                    url=item.get("url", "https://example.com"),
                    snippet=item.get("text", ""),
                    published_at=published_at,
                    source=item.get("domain", ""),
                )
            )
        except Exception:
            # Skip malformed entries
            continue
    # If no articles were parsed, return mock data so the agent has
    # something to work with.
    if not out:
        return _mock_articles(params.query, params.num_results)
    return out


async def news_summarizer(
    articles: List[Article],
    tone: Optional[str] = None,
    fmt: Optional[str] = None,
    language: Optional[str] = None,
    interaction: Optional[str] = None,
) -> str:
    """
    Summarise a list of articles according to user preferences.

    If `MOCK_MODE` is true, this function constructs a simple
    summary from the titles and sources of the articles. It
    optionally formats the summary as bullets or paragraphs. When
    not in mock mode, it would normally call a language model, but
    since external network access is restricted here, it falls back
    to the same deterministic logic.
    """
    if not articles:
        return "I couldn't find any articles on that topic."

    # Build a list of lines describing each article. Include title
    # and source. In a real implementation you might include
    # published dates or snippets.
    lines = [f"{art.title} ({art.source})" for art in articles]

    # Determine the prefix based on tone. This is a simplistic
    # illustration; real tone adjustments would be more nuanced.
    if tone == "formal":
        greeting = "Here is a formal summary of the latest articles:"
    elif tone == "enthusiastic":
        greeting = "Great news! Here are some exciting headlines:"
    else:  # default to casual
        greeting = "Here's what I found:"

    # Format according to the desired output style.
    if fmt == "bullets":
        summary_body = "\n".join([f"- {line}" for line in lines])
    else:
        # Paragraph format: join lines with spaces.
        summary_body = " ".join(lines)

    # Compose the final summary. Interaction level could influence
    # verbosity, but here we only differentiate between concise and
    # detailed by including more or fewer articles.
    if interaction == "detailed":
        body = summary_body
    else:
        # Concise: include only the first few items
        max_items = 3
        truncated = lines[:max_items]
        if fmt == "bullets":
            body = "\n".join([f"- {line}" for line in truncated])
        else:
            body = " ".join(truncated)
    # Note: language preference is ignored in this mock
    return f"{greeting}\n{body}"