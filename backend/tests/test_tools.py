"""
Unit tests for the agent's tool implementations.

These tests run in mock mode to avoid any external network calls.
They verify that the news fetcher returns the expected number of
articles and that the summariser produces summaries respecting
preferences.
"""

import asyncio

import os

from agent.tools import exa_news_fetcher, news_summarizer
from agent.schemas import FetchParams, Article


def test_mock_fetcher_returns_correct_count(monkeypatch):
    """Ensure the mock fetcher returns the requested number of articles."""
    # Force mock mode regardless of environment
    monkeypatch.setenv("MOCK_MODE", "true")
    params = FetchParams(query="chips", num_results=4)
    articles = asyncio.run(exa_news_fetcher(params))
    assert len(articles) == 4
    assert all(isinstance(a, Article) for a in articles)


def test_news_summarizer_bullets(monkeypatch):
    """Verify that the summariser returns a bullet formatted summary."""
    monkeypatch.setenv("MOCK_MODE", "true")
    # Create sample articles manually
    articles = [
        Article(title=f"Title {i}", url="https://example.com", source="example.com")
        for i in range(1, 4)
    ]
    summary = asyncio.run(
        news_summarizer(
            articles=articles,
            tone="formal",
            fmt="bullets",
            language="en",
            interaction="concise",
        )
    )
    # Expect bullet points to start with a hyphen
    lines = summary.splitlines()
    assert any(line.startswith("- ") for line in lines), "Summary should contain bullet points"
    assert "formal" not in summary.lower(), "Tone should influence greeting, not appear verbatim"